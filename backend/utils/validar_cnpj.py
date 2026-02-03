import re

def limpar_cnpj(cnpj: str) -> str:
    return re.sub(r"\D", "", cnpj)

def cnpj_valido(cnpj: str) -> bool:
    return len(cnpj) == 14