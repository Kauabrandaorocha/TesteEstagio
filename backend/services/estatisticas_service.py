from db import get_db_connection

def calcular_estatisticas():
    conn = get_db_connection()
    cur = conn.cursor()

    # total e média
    cur.execute("""
        SELECT
            SUM(valor_despesas),
            AVG(valor_despesas)
        FROM consolidado_despesas;
    """)
    total, media = cur.fetchone()

    # top 5 operadoras
    cur.execute("""
        SELECT
            razao_social,
            SUM(valor_despesas) AS total
        FROM consolidado_despesas
        GROUP BY razao_social
        ORDER BY total DESC
        LIMIT 5;
    """)
    top_operadoras = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "total_despesas": float(total) if total else 0,
        "media_despesas": float(media) if media else 0,
        "top_5_operadoras": [
            {
                "razao_social": row[0],
                "total_despesas": float(row[1])
            }
            for row in top_operadoras
        ]
    }