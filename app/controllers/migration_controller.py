import logging
import datetime
import sys
import json
import time
from app.models.database import get_prod_connection, get_homolog_connection
from core.config import rows_env
from app.controllers.structure_controller import StructureController
from core.utils import is_valid_date
from tqdm import tqdm
from core.config import getAllTablesMigration
from psycopg2.extras import execute_batch


class MigrationController:
    def __init__(self, prod_db, homolog_db, pg_bin_path, logger):
        self.prod_db = prod_db
        self.homolog_db = homolog_db
        self.pg_bin_path = pg_bin_path
        self.logger = logger
        self.structure_controller = StructureController(prod_db, homolog_db, pg_bin_path, logger)
        self.prod_conn = self.prod_cur = None
        self.homolog_conn = self.homolog_cur = None
        self.start_time = time.time()
        self.batch_size = 1000
        self.verbose_mode = "-v" in sys.argv or "--verbose" in sys.argv

        if self.verbose_mode:
            logging.getLogger().setLevel(logging.DEBUG)
            logging.debug("Modo verbose ativado.")
        else:
            logging.getLogger().setLevel(logging.INFO)

    def run_migration(self, quantidade=None):
        try:
            self.prod_conn, self.prod_cur = get_prod_connection()
            self.homolog_conn, self.homolog_cur = get_homolog_connection()

            self.disable_constraints()
            self.migrate_tables(quantidade)
            self.enable_constraints()

            logging.info(f"Migração concluída com sucesso em: {datetime.datetime.now()}")
        except Exception as e:
            logging.error(f"Erro durante a migração: {e}")
            raise
        finally:
            if self.prod_conn:
                self.prod_conn.close()
            if self.homolog_conn:
                self.homolog_cur.close()
                self.homolog_conn.close()

    def disable_constraints(self):
        self.homolog_cur.execute("SET session_replication_role = 'replica'")
        self.homolog_cur.execute("SET CONSTRAINTS ALL DEFERRED;")
        self.homolog_conn.commit()
        if self.verbose_mode:
            logging.debug("Constraints desativadas.")

    def migrate_tables(self, row_limit=None):
        self.prod_cur.execute(getAllTablesMigration)
        tables_production = self.prod_cur.fetchall()
        total_tables = len(tables_production)

        main_progress = tqdm(
            tables_production,
            desc="🔄 Migrando tabelas",
            total=total_tables,
            unit="tabela",
            colour="cyan",
            position=0,
            file=sys.stderr
        )

        for index, (table_name,) in enumerate(main_progress, 1):
            main_progress.set_description(f"📥 Migrando: \033[92m{table_name}\033[0m")
            self._process_table(table_name, index, total_tables, main_progress, row_limit)

        main_progress.close()

        seq_progress = tqdm(
            tables_production,
            desc="🔄 Atualizando sequências",
            total=total_tables,
            unit="tabela",
            colour="blue",
            position=0,
            file=sys.stderr
        )

        for index, (table_name,) in enumerate(seq_progress, 1):
            self._update_sequences(table_name, index, total_tables, seq_progress)

        seq_progress.close()

    def _process_table(self, table_name, index, total_tables, main_progress, row_limit):
        try:
            self.prod_cur.execute(f"""
                SELECT 
                    a.attname as column_name, 
                    format_type(a.atttypid, a.atttypmod) as data_type,
                    a.attnotnull as is_not_null
                FROM pg_index i
                JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                WHERE i.indrelid = '\"{table_name}\"'::regclass AND i.indisprimary;
            """)
            pk_info = self.prod_cur.fetchall()
            pk_columns = [row[0] for row in pk_info]
            col_types = {row[0]: row[1] for row in pk_info}

            self.prod_cur.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
            """)
            col_types.update(dict(self.prod_cur.fetchall()))

            order_by = ', '.join([f'"{col}"' for col in pk_columns]) if pk_columns else 'ctid'
            query = f'SELECT * FROM "{table_name}" ORDER BY {order_by}'

            if row_limit is not None:
                query += f" LIMIT {row_limit}"
            elif rows_env:
                query += f" LIMIT {rows_env}"

            self.prod_cur.execute(query)

            columns = [desc[0] for desc in self.prod_cur.description]
            columns_list = ', '.join([f'"{col}"' for col in columns])
            placeholders = ', '.join(['%s'] * len(columns))

            insert_query = f"""
                INSERT INTO "{table_name}" ({columns_list})
                VALUES ({placeholders})
                ON CONFLICT DO NOTHING
            """

            self.homolog_cur.execute(f'ALTER TABLE "{table_name}" DISABLE TRIGGER ALL;')
            self.homolog_conn.commit()

            total_rows = 0
            total_bytes = 0

            with tqdm(
                    desc=f"💾 Processando {table_name}",
                    unit=" linhas",
                    leave=False,
                    colour="green",
                    position=1,
                    file=sys.stderr
            ) as row_progress:

                while True:
                    rows = self.prod_cur.fetchmany(size=self.batch_size)
                    if not rows:
                        break

                    processed_batch = []
                    for row in rows:
                        processed_row = [
                            self._format_value(col, val, col_types.get(col, ''), table_name)
                            for col, val in zip(columns, row)
                        ]
                        processed_batch.append(processed_row)
                        total_bytes += sum(len(str(val)) if val is not None else 0 for val in row)

                    execute_batch(self.homolog_cur, insert_query, processed_batch)
                    self.homolog_conn.commit()

                    total_rows += len(rows)
                    row_progress.update(len(rows))
                    row_progress.set_postfix(
                        rows=total_rows,
                        size=self._human_readable_size(total_bytes)
                    )

            self.homolog_cur.execute(f'ALTER TABLE "{table_name}" ENABLE TRIGGER ALL;')
            self.homolog_conn.commit()

            main_progress.write(
                f"✅ [{index:>3}/{total_tables}]: "
                f"{total_rows:>6} registros, "
                f"{self._human_readable_size(total_bytes):>10} copiados, "
                f"tabela: \033[92m{table_name}\033[0m"
            )

        except Exception as e:
            logging.error(f"Erro ao processar tabela {table_name}: {e}")
            self.homolog_conn.rollback()
            raise

    def _update_sequences(self, table_name, index, total_tables, progress):
        self.prod_cur.execute(getAllTablesMigration)
        tables_production = self.prod_cur.fetchall()
        progress.set_description(
            f"🔄️ Atualizando sequência da tabela: \033[92m{table_name}\033[0m"
        )

        self.homolog_cur.execute(f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            AND column_default LIKE 'nextval(%'
        """)
        seq_columns = self.homolog_cur.fetchall()

        for (col,) in seq_columns:
            self.homolog_cur.execute(f"""
                DO $$
                DECLARE
                    seq_name TEXT;
                BEGIN
                    SELECT pg_get_serial_sequence('"{table_name}"', '{col}') INTO seq_name;

                    IF seq_name IS NOT NULL THEN
                        EXECUTE format(
                            'SELECT setval(''%s'', COALESCE((SELECT MAX("{col}") + 1 FROM "{table_name}"), 1), false)',
                            seq_name
                        );
                    END IF;
                END $$;
            """)
            self.homolog_conn.commit()

        progress.write(
            f"✅ Sequence {index:03}/{total_tables:03}: \033[92m{table_name}\033[0m"
        )

        if table_name == tables_production[-1][0]:
            progress.set_description("✅ Atualização de sequências concluída!")
            progress.refresh()
            progress.close()

    def enable_constraints(self):
        try:
            self.homolog_cur.execute("SET session_replication_role = 'origin'")
            self.homolog_cur.execute("SET CONSTRAINTS ALL IMMEDIATE;")
            self.homolog_conn.commit()
            if self.verbose_mode:
                logging.debug("Constraints reativadas.")
        except Exception as e:
            logging.error(f"Erro ao ativar constraints: {e}")
            self.homolog_conn.rollback()
            raise

    def _format_value(self, col, val, col_type, table_name):
        import datetime
        import json

        if val is None:
            return None
        try:
            # JSON e JSONB
            if col_type in ('json', 'jsonb'):
                return json.dumps(val) if not isinstance(val, str) else val
            # Arrays
            elif col_type.startswith('ARRAY') or col_type.startswith('_'):
                if col_type == '_int4':
                    return '{' + ','.join(map(str, val)) + '}'
                return '{"' + '","'.join(map(str, val)) + '"}'
            # Datas
            elif col_type == 'date':
                if not is_valid_date(val):
                    logging.error(
                        f"Data inválida encontrada: {val} na tabela {table_name}, coluna {col}. Substituída por 2025-01-01.")
                    return '2025-01-01'
                if isinstance(val, datetime.datetime):
                    return val.strftime('%Y-%m-%d')
                return val
            # Timestamps
            elif col_type == 'timestamp without time zone' or 'timestamp' in col_type:
                if not is_valid_date(val):
                    logging.error(
                        f"Timestamp inválido encontrado: {val} na tabela {table_name}, coluna {col}. Substituído por 2025-01-01 00:00:00.")
                    return '2025-01-01 00:00:00'
                if isinstance(val, datetime.datetime):
                    return val.strftime('%Y-%m-%d %H:%M:%S')
                return val
            # Outros tipos
            else:
                return val
        except Exception as e:
            logging.error(
                f"Erro ao processar valor: {val} na tabela {table_name}, coluna {col}. Detalhes: {e}")
            return None

    def _human_readable_size(self, num):
        for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if num < 1024:
                return f"{num:.2f} {unit}"
            num /= 1024
        return f"{num:.2f} PB"
