from core.config import prod_db, homolog_db
import psycopg2

def get_prod_connection():
    conn = psycopg2.connect(**prod_db)
    return conn, conn.cursor()

def get_homolog_connection():
    conn = psycopg2.connect(**homolog_db)
    return conn, conn.cursor()
