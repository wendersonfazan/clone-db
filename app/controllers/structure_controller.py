from tqdm import tqdm
import os
import subprocess
import psycopg2
import logging
import sys
from typing import Dict


class StructureController:
    def __init__(self, prod_db: Dict, homolog_db: Dict, pg_bin_path: str, logger: logging.Logger):
        self.prod_db = prod_db
        self.homolog_db = homolog_db
        self.pg_bin_path = pg_bin_path
        self.logger = logger

        self.envProd = {**os.environ, "PGPASSWORD": prod_db["password"]}
        self.envHomo = {**os.environ, "PGPASSWORD": homolog_db["password"]}

    def drop_and_recreate_homolog_db(self):
        try:
            self.terminate_connections()

            tasks = self.build_tasks()

            pbar = tqdm(
                tasks,
                desc="🔧 Preparando banco de homologação",
                unit="etapa",
                leave=True,
                colour="WHITE",
                bar_format="{l_bar}{bar} {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
                file=sys.stderr
            )

            for description, command, env in pbar:
                pbar.set_description(f"🔄️ {description}")
                subprocess.run(command, check=True, env=env)
                pbar.write(f"✅ {description}")

            pbar.set_description("✅ Banco de homologação pronto para uso!")
            pbar.write("🎉 Processo finalizado com sucesso!")
            pbar.close()

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Erro ao executar comando: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Erro inesperado: {e}")
            raise

    def terminate_connections(self):
        """Encerra conexões ativas no banco de homologação."""
        try:
            conn = psycopg2.connect(
                host=self.homolog_db["host"],
                dbname=self.homolog_db["dbname"],
                user=self.homolog_db["user"],
                password=self.homolog_db["password"],
                port=self.homolog_db["port"]
            )
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = %s
                    AND pid <> pg_backend_pid();
                """, (self.homolog_db["dbname"],))
            conn.close()
            self.logger.info("Conexões ativas terminadas com sucesso.")
        except Exception as e:
            self.logger.error(f"Erro ao encerrar conexões: {e}")
            raise

    def build_tasks(self):
        return [
            ("Removendo banco de homologação...", [
                os.path.join(self.pg_bin_path, 'dropdb.exe'),
                '-h', self.homolog_db['host'],
                '-U', self.homolog_db['user'],
                self.homolog_db['dbname']
            ], self.envHomo),
            ("Criando novo banco de homologação...", [
                os.path.join(self.pg_bin_path, 'createdb.exe'),
                '-h', self.homolog_db['host'],
                '-U', self.homolog_db['user'],
                self.homolog_db['dbname']
            ], self.envHomo),
            ("Exportando estrutura do banco de produção...", [
                os.path.join(self.pg_bin_path, 'pg_dump.exe'),
                '-h', self.prod_db['host'],
                '-U', self.prod_db['user'],
                '-s', '--no-owner', '--no-acl', '--no-comments',
                '-f', 'estrutura.sql',
                self.prod_db['dbname']
            ], self.envProd),
            ("Importando estrutura no banco de homologação...", [
                os.path.join(self.pg_bin_path, 'psql.exe'),
                '-h', self.homolog_db['host'],
                '-U', self.homolog_db['user'],
                '-d', self.homolog_db['dbname'],
                '-f', 'estrutura.sql'
            ], self.envHomo)
        ]
