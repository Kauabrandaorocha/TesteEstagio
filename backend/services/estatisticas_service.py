from db import get_db_connection

def calcular_estatisticas():
    conn = get_db_connection()
    cur = conn.cursor()

    # 1. Total e Média Geral
    cur.execute("""
        SELECT SUM(valor_despesas), AVG(valor_despesas)
        FROM consolidado_despesas;
    """)
    total, media = cur.fetchone()

    # 2. Top 5 Operadoras (Maior despesa)
    cur.execute("""
        SELECT razao_social, SUM(valor_despesas) AS total
        FROM consolidado_despesas
        GROUP BY razao_social
        ORDER BY total DESC
        LIMIT 5;
    """)
    top_operadoras = cur.fetchall()

    # 3. Distribuição por UF (Para o Gráfico)
    # Precisamos fazer um JOIN porque a UF está em 'dados_cadastrais' 
    # e o valor em 'consolidado_despesas'
    cur.execute("""
    SELECT d.uf, SUM(c.valor_despesas) as total
    FROM dados_cadastrais d
    JOIN consolidado_despesas c ON d.CNPJ = c.CNPJ
    GROUP BY d.uf
    ORDER BY total DESC;
    """)
    despesas_por_uf = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "total_despesas": float(total) if total else 0,
        "media_despesas": float(media) if media else 0,
        "top_5_operadoras": [
            {"razao_social": row[0], "total_despesas": float(row[1])} for row in top_operadoras
        ],
        "despesas_por_uf": [
            {"uf": row[0], "total": float(row[1])} for row in despesas_por_uf
        ]
    }