import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)

cur = conn.cursor()

def run_sql(path):
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read().strip()
        if sql:
            cur.execute(sql)

run_sql("../supabase/00_drop_all.sql")
run_sql("../supabase/01_ddl.sql")
run_sql("../supabase/02_indices.sql")
conn.commit()


def copy_csv(table, csv_path):
    with open(csv_path, "r", encoding="utf-8") as f:
        cur.copy_expert(
            f"""
            COPY {table}
            FROM STDIN
            WITH (
                FORMAT csv,
                HEADER true,
                DELIMITER ';',
                ENCODING 'UTF8'
            )
            """,
            f
        )
copy_csv("staging_consolidado_despesas", "../consolidado_despesas/consolidado_despesas.csv")
copy_csv("staging_dados_cadastrais", "../dados_cadastrais/Relatorio_cadop.csv")
copy_csv("staging_despesas_agregadas", "../despesas_agregadas/despesas_agregadas.csv")

run_sql("../supabase/03_validacoes.sql")

conn.commit()

run_sql("../supabase/04_queries_analiticas.sql")
conn.commit()

cur.close()
conn.close()