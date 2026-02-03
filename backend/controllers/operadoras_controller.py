from db import get_db_connection
from services import operadoras_service
from utils import validar_cnpj


def lista_operadoras(page, limit):
    offset = (page - 1) * limit

    conn = get_db_connection()
    cur = conn.cursor()

    total = operadoras_service.contar_operadoras(cur)
    rows = operadoras_service.listar_operadoras(cur, limit, offset)

    cur.close()
    conn.close()

    data = [
        {"cnpj": r[0], "razao_social": r[1], "uf": r[2]}
        for r in rows
    ]

    return {
        "data": data,
        "meta": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    }


def detalhe_operadora(cnpj):
    cnpj_limpo = validar_cnpj.limpar_cnpj(cnpj)

    if not validar_cnpj.cnpj_valido(cnpj_limpo):
        return None, "CNPJ inválido"

    conn = get_db_connection()
    cur = conn.cursor()

    row = operadoras_service.buscar_operadora_por_cnpj(cur, cnpj_limpo)

    cur.close()
    conn.close()

    if not row:
        return None, "Operadora não encontrada"

    operadora = {
        "cnpj": row[0],
        "registro_operadora": row[1],
        "razao_social": row[2],
        "nome_fantasia": row[3],
        "modalidade": row[4],
        "logradouro": row[5],
        "numero": row[6],
        "complemento": row[7],
        "bairro": row[8],
        "cidade": row[9],
        "uf": row[10],
        "cep": row[11],
        "ddd": row[12],
        "telefone": row[13],
        "fax": row[14],
        "endereco_eletronico": row[15],
        "representante": row[16],
        "cargo_representante": row[17],
        "regiao_de_comercializacao": row[18],
        "data_registro_ans": row[19]
    }

    return operadora, None


def despesas_operadora(cnpj, page, limit):
    cnpj_limpo = validar_cnpj.limpar_cnpj(cnpj)

    if not validar_cnpj.cnpj_valido(cnpj_limpo):
        return None, "CNPJ inválido"

    offset = (page - 1) * limit

    conn = get_db_connection()
    cur = conn.cursor()

    total = operadoras_service.contar_despesas(cur, cnpj_limpo)
    rows = operadoras_service.listar_despesas(cur, cnpj_limpo, limit, offset)

    cur.close()
    conn.close()

    despesas = [
        {
            "ano": r[0],
            "trimestre": r[1],
            "valor_despesas": float(r[2]) if r[2] else None
        }
        for r in rows
    ]

    return {
        "cnpj": cnpj_limpo,
        "data": despesas if despesas else ["Nao foi encontrado no banco despesas relacionadas a operadora solicitada."],
        "meta": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    }, None