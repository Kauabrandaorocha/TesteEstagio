def contar_operadoras(cur):
    cur.execute("SELECT COUNT(*) FROM dados_cadastrais;")
    return cur.fetchone()[0]


def listar_operadoras(cur, limit, offset):
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
    cur.execute("""
        SELECT COUNT(*)
        FROM consolidado_despesas
        WHERE cnpj = %s;
    """, (cnpj,))
    return cur.fetchone()[0]


def listar_despesas(cur, cnpj, limit, offset):
    cur.execute("""
        SELECT
            ano,
            trimestre,
            valor_despesas
        FROM consolidado_despesas
        WHERE cnpj = %s
        ORDER BY ano DESC, trimestre DESC
        LIMIT %s OFFSET %s;
    """, (cnpj, limit, offset))
    return cur.fetchall()