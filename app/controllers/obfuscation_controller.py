from app.models.database import get_homolog_connection
from core.config import rows_env
from core.obfuscation_config import OBFUSCATION_TABLES
from tqdm import tqdm
import logging
import sys

class ObfuscationController:
    def __init__(self, homolog_db, logger):
        self.homolog_conn, self.homolog_cur = get_homolog_connection()
        self.logger = logger
        sys.stdout = sys.__stdout__

    def run_obfuscation(self):
        self.logger.info("Iniciando o processo de ofuscação.")
        for conf in OBFUSCATION_TABLES:
            self.process_table(conf)

    def process_table(self, conf):
        table = conf["table"]
        try:
            query = conf["select"] + (f" LIMIT {rows_env};" if rows_env else ";")
            self.homolog_cur.execute(query)
            rows = self.homolog_cur.fetchall()

            for row in tqdm(rows, desc=f"Ofuscando: \033[93m[{table}]\033[0m", file=sys.stderr):
                try:
                    new_data = conf["generate"](row)
                    self.homolog_cur.execute(conf["update"], new_data)
                except Exception as row_err:
                    logging.error(f"Erro ao atualizar linha da tabela {table}: {row_err}")
                    self.homolog_conn.rollback()

            self.homolog_conn.commit()
            logging.info(f"Tabela {table} ofuscada com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao processar tabela {table}: {e}")
            self.homolog_conn.rollback()
