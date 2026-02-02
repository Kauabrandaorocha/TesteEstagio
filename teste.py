# ...existing code...
import os
import re
import logging
import pandas as pd

# Configuração de logging
logger = logging.getLogger("validador_cnpj")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

def normalizar_cnpj(valor):
    """Remove caracteres não numéricos; retorna string vazia se ausente."""
    if pd.isna(valor):
        return ""
    return re.sub(r"\D", "", str(valor))

def todos_digitos_iguais(digs):
    """Retorna True se todos os dígitos da string forem iguais (ex: '111111...')."""
    if not digs:
        return False
    return digs == digs[0] * len(digs)

def tem_sequencia_repetida(digs, minimo=6):
    """Detecta sequências consecutivas do mesmo dígito com comprimento >= minimo."""
    if not digs:
        return False
    pattern = rf"(\d)\1{{{minimo-1},}}"
    return bool(re.search(pattern, digs))

def cnpj_checksum_valido(cnpj):
    """Valida os dígitos verificadores do CNPJ (algoritmo módulo 11)."""
    if len(cnpj) != 14 or not cnpj.isdigit():
        return False
    if todos_digitos_iguais(cnpj):
        return False

    def calc(digs, pesos):
        s = sum(int(d) * w for d, w in zip(digs, pesos))
        r = s % 11
        return '0' if r < 2 else str(11 - r)

    pesos1 = [5,4,3,2,9,8,7,6,5,4,3,2]
    pesos2 = [6] + pesos1
    d1 = calc(cnpj[:12], pesos1)
    d2 = calc(cnpj[:12] + d1, pesos2)
    return (d1 == cnpj[12]) and (d2 == cnpj[13])

def validar_cnpj(valor):
    """
    Valida um CNPJ e retorna (booleano_valido, motivo).
    Motivos: 'missing', 'invalid_length', 'non_digit', 'all_same_digits',
             'repeated_sequence', 'invalid_checksum', 'valid'
    """
    norm = normalizar_cnpj(valor)
    if norm == "":
        return False, "missing"
    if len(norm) != 14:
        return False, "invalid_length"
    if not norm.isdigit():
        return False, "non_digit"
    if todos_digitos_iguais(norm):
        return False, "all_same_digits"
    if tem_sequencia_repetida(norm, minimo=6):
        return False, "repeated_sequence"
    if not cnpj_checksum_valido(norm):
        return False, "invalid_checksum"
    return True, "valid"

def validar_cnpjs_da_pasta(diretorio):
    """
    Lê o CSV consolidado na pasta informada, valida a coluna CNPJ e retorna o DataFrame
    com colunas adicionais de diagnóstico. NÃO salva novo CSV (apenas valida).
    Args:
        diretorio (str): caminho da pasta que contém 'consolidado_despesas.csv' (ou 'consolidado.csv').
    Retorna:
        pd.DataFrame com colunas: CNPJ, cnpj_normalizado, cnpj_valido (bool), motivo_invalidez (str)
    """
    nomes_possiveis = ["consolidado_despesas.csv", "consolidado.csv"]
    caminho_csv = None
    for nome in nomes_possiveis:
        p = os.path.join(diretorio, nome)
        if os.path.exists(p):
            caminho_csv = p
            break
    if caminho_csv is None:
        logger.error("Arquivo consolidado não encontrado na pasta: %s", diretorio)
        return None

    logger.info("Lendo arquivo consolidado: %s", caminho_csv)
    df = pd.read_csv(caminho_csv, sep=';', dtype=str, encoding='utf-8-sig')

    # garantir existência da coluna CNPJ
    if 'CNPJ' not in df.columns:
        logger.warning("Coluna 'CNPJ' não encontrada no CSV; coluna será criada com valores vazios.")
        df['CNPJ'] = ""

    # normalizar e validar
    logger.info("Normalizando CNPJ e executando validação...")
    df['cnpj_normalizado'] = df['CNPJ'].apply(normalizar_cnpj)
    resultados = df['cnpj_normalizado'].apply(validar_cnpj)
    df['cnpj_valido'] = resultados.apply(lambda t: t[0])
    df['motivo_invalidez'] = resultados.apply(lambda t: t[1])

    # sumarizar resultado e logs de diagnóstico
    total = len(df)
    validos = int(df['cnpj_valido'].sum())
    invalidos = total - validos
    distribuicao_motivos = df['motivo_invalidez'].value_counts().to_dict()

    logger.info("Validação concluída: total=%d, válidos=%d, inválidos=%d", total, validos, invalidos)
    logger.info("Distribuição de motivos de invalidez: %s", distribuicao_motivos)

    # mostrar exemplos dos inválidos para inspeção (até 5)
    invalid_examples = df.loc[~df['cnpj_valido'], ['CNPJ', 'cnpj_normalizado', 'motivo_invalidez']].head(5)
    if not invalid_examples.empty:
        logger.info("Exemplos de CNPJs inválidos (até 5):\n%s", invalid_examples.to_string(index=False))
    else:
        logger.info("Nenhum CNPJ inválido encontrado (todos vazios ou válidos conforme critérios).")

    # Retorna o dataframe com as colunas de validação (sem salvar arquivo)
    return df

if __name__ == "__main__":
    # Exemplo de uso: passar o diretório que contém o consolidado_despesas.csv
    pasta_atual = os.path.dirname(os.path.abspath(__file__))
    pasta_consolidado = os.path.join(pasta_atual, "consolidado_despesas")
    df_resultado = validar_cnpjs_da_pasta(pasta_consolidado)
    if df_resultado is not None:
        logger.info("Processamento finalizado; DataFrame com validações retornado.")
# ...existing code...