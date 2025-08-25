from dotenv import load_dotenv
import os

load_dotenv()

rows_env = int(os.getenv("ROWS_LIMIT", 10000))

prod_db = {
    "host": os.getenv("PROD_DB_HOST"),
    "dbname": os.getenv("PROD_DB_NAME"),
    "user": os.getenv("PROD_DB_USER"),
    "password": os.getenv("PROD_DB_PASSWORD"),
    "port": os.getenv("PROD_DB_PORT"),
    "application_name": os.getenv("PROD_DB_APP_NAME"),
    "sslmode": "disable",
    "connect_timeout": 60
}

homolog_db = {
    "host": os.getenv("HOMOLOG_DB_HOST"),
    "dbname": os.getenv("HOMOLOG_DB_NAME"),
    "user": os.getenv("HOMOLOG_DB_USER"),
    "password": os.getenv("HOMOLOG_DB_PASSWORD"),
    "port": os.getenv("HOMOLOG_DB_PORT"),
    "application_name": os.getenv("HOMOLOG_DB_APP_NAME"),
    "sslmode": "disable",
    "connect_timeout": 60
}

pg_bin_path = r'C:\Program Files\PostgreSQL\17\bin'

getAllTablesMigration = "SELECT tablename FROM pg_tables WHERE schemaname = 'public'  and tablename not in ('temp', 'temporary') ORDER BY tablename"