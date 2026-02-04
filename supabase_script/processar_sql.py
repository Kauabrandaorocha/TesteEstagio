import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# --- MAPEAMENTO DE DIRETÓRIOS ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJETO_ROOT = os.path.dirname(SCRIPT_DIR)
PASTA_DADOS = os.path.join(PROJETO_ROOT, 'arquivos_csv_zips')
PASTA_SQL = os.path.join(PROJETO_ROOT, 'supabase') # Onde estão seus arquivos .sql

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)
cur = conn.cursor()

def run_sql(filename):
    path = os.path.join(PASTA_SQL, filename)
    if not os.path.exists(path):
        print(f"Aviso: Arquivo SQL não encontrado: {filename}")
        return
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read().strip()
        if sql:
            cur.execute(sql)

# 1. Preparar Esquema
run_sql("00_drop_all.sql")
run_sql("01_ddl.sql")
run_sql("02_indices.sql")
conn.commit()

# 2. Importação de Dados
def copy_csv(table, relative_csv_path):
    # Constrói o caminho completo a partir da PASTA_DADOS
    csv_path = os.path.join(PASTA_DADOS, relative_csv_path)
    
    if not os.path.exists(csv_path):
        print(f"Erro: Arquivo CSV não encontrado para a tabela {table}: {csv_path}")
        return

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
    print(f"Dados copiados para {table} com sucesso.")

# --- AJUSTE DOS CAMINHOS DOS CSVS ---
copy_csv("staging_consolidado_despesas", "consolidado_despesas/consolidado_despesas.csv")
copy_csv("staging_dados_cadastrais", "dados_cadastrais/Relatorio_cadop.csv")
copy_csv("staging_despesas_agregadas", "despesas_agregadas/despesas_agregadas.csv")

# 3. Rodar Validações e Queries
run_sql("03_validacoes.sql")
conn.commit()
run_sql("04_queries_analiticas.sql")
conn.commit()

cur.close()
conn.close()