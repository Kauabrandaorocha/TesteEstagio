def contar_operadoras(cur, search_term=None):
    # Garante que se search_term for None ou vazio, não entre no filtro
    if search_term and search_term.strip():
        query = """
            SELECT COUNT(*) 
            FROM dados_cadastrais 
            WHERE razao_social ILIKE %s 
               OR CAST(cnpj AS TEXT) ILIKE %s;
        """
        term = f"%{search_term.strip()}%"
        cur.execute(query, (term, term))
    else:
        cur.execute("SELECT COUNT(*) FROM dados_cadastrais;")
    
    return cur.fetchone()[0]


def listar_operadoras(cur, limit, offset, search_term=None):
    if search_term and search_term.strip():
        query = """
            SELECT cnpj, razao_social, uf
            FROM dados_cadastrais
            WHERE razao_social ILIKE %s OR cnpj ILIKE %s
            ORDER BY razao_social
            LIMIT %s OFFSET %s
        """
        term = f"%{search_term.strip()}%"
        cur.execute(query, (term, term, limit, offset))
    else:
        cur.execute("""
            SELECT cnpj, razao_social, uf
            FROM dados_cadastrais
            ORDER BY razao_social
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
    return cur.fetchall()


def buscar_operadora_por_cnpj(cur, cnpj):
    cur.execute("""
        SELECT
            cnpj,
            registro_operadora,
            razao_social,
            nome_fantasia,
            modalidade,
            logradouro,
            numero,
            complemento,
            bairro,
            cidade,
            uf,
            cep,
            ddd,
            telefone,
            fax,
            endereco_eletronico,
            representante,
            cargo_representante,
            regiao_de_comercializacao,
            data_registro_ans
        FROM dados_cadastrais
        WHERE cnpj = %s;
    """, (cnpj,))
    return cur.fetchone()


def contar_despesas(cur, cnpj):
    cnpj_limpo = "".join(filter(str.isdigit, cnpj)).zfill(14)
    cur.execute("""
        SELECT COUNT(*)
        FROM consolidado_despesas
        WHERE cnpj = %s;
    """, (cnpj_limpo,))
    return cur.fetchone()[0]


def listar_despesas(cur, cnpj_limpo, limit, offset):
    cnpj_formatado = cnpj_limpo.zfill(14) 
    
    cur.execute("""
        SELECT ano, trimestre, valor_despesas
        FROM consolidado_despesas
        WHERE cnpj = %s
        ORDER BY ano DESC, trimestre DESC
        LIMIT %s OFFSET %s;
    """, (cnpj_formatado, limit, offset))
    return cur.fetchall()

def obter_indicadores_financeiros(cur, cnpj_limpo):
    query = """
        SELECT 
            COALESCE(SUM(valor_despesas), 0), 
            COALESCE(AVG(valor_despesas), 0),
            COUNT(DISTINCT ano)
        FROM consolidado_despesas 
        WHERE cnpj = %s
    """
    cur.execute(query, (cnpj_limpo,))
    res = cur.fetchone()
    
    return {
        "total_valor": float(res[0]),
        "media_valor": float(res[1]),
        "anos_ativos": int(res[2])
    }