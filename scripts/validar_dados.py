import os
import re
import logging
import pandas as pd

# Retorna um objeto Logger com o nome "validador_cnpj"
logger = logging.getLogger("validador_cnpj")
# logs para debug
logger.setLevel(logging.INFO)
# criar um manipulador para exibir os logs no console
handler = logging.StreamHandler()
# definir o formato dos logs
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
# adicionar o manipulador ao logger
logger.addHandler(handler)

class ValidadorDados:
    def __init__(self, logger=None):
        # a classe ira usar esse logger que foi configurado acima, internamente nela
        self.logger = logger or logging.getLogger(__name__)

    # CNPJ
    def normalizar_cnpj(self, valor):
        if pd.isna(valor):
            return ""
        return re.sub(r"\D", "", str(valor))

    def todos_digitos_iguais(self, digitos):
        if not digitos:
            return False
        return digitos == digitos[0] * len(digitos)

    def tem_sequencia_repetida(self, digitos, minimo=6):
        if not digitos:
            return False
        pattern = rf"(\d)\1{{{minimo-1},}}"
        return bool(re.search(pattern, digitos))

    def checagem_cnpj_valido(self, cnpj):
        if len(cnpj) != 14 or not cnpj.isdigit():
            return False
        if self.todos_digitos_iguais(cnpj):
            return False

        def calc(digitos, pesos):
            # efetua o cálculo do dígito verificador
            soma = sum(int(d) * w for d, w in zip(digitos, pesos))
            r = soma % 11
            return '0' if r < 2 else str(11 - r)
        
        # pesos padrões do cnpj
        pesos1 = [5,4,3,2,9,8,7,6,5,4,3,2]
        pesos2 = [6] + pesos1

        # pesos utilizados para calcular os dígitos verificadores
        d1 = calc(cnpj[:12], pesos1)
        d2 = calc(cnpj[:12] + d1, pesos2)
        return (d1 == cnpj[12]) and (d2 == cnpj[13])

    def validar_cnpj(self, valor):
        norm = self.normalizar_cnpj(valor)
        if norm == "":
            return False, "missing"
        if len(norm) != 14:
            return False, "tamanho_invalido"
        if not norm.isdigit():
            return False, "nao_digito"
        if self.todos_digitos_iguais(norm):
            return False, "todos_iguais"
        if self.tem_sequencia_repetida(norm, minimo=6):
            return False, "sequencia_repetida"
        if not self.checagem_cnpj_valido(norm):
            return False, "digitos_invalidos"
        return True, "valid"

    # VALOR POSITIVO
    def parse_num(self, valor):
        if pd.isna(valor):
            return None
        string = str(valor).strip()
        if string == "":
            return None
        # tentativa simples para formatos BR: 1.234,56 -> 1234.56
        string = string.replace(".", "").replace(",", ".")
        try:
            return float(string)
        except Exception:
            try:
                return float(re.sub(r"[^\d\.\-]", "", string))
            except Exception:
                return None

    def validar_valor_positivo(self, valor):
        num = self.parse_num(valor)
        if num is None:
            return False, "missing_or_nao_numerico"
        if num <= 0:
            return False, "nao_positivo"
        return True, "valido"

    # RAZÃO SOCIAL
    def validar_razao_social(self, valor):
        if pd.isna(valor):
            return False, "missing"
        s = str(valor).strip()
        if s == "":
            return False, "empty"
        return True, "valido"

    # PROCESSAMENTO DO CSV CONSOLIDADO
    def validar_arquivo_consolidado(self, input_dir, output_dir=None):
        """Valida o arquivo consolidado localizado em input_dir.
        Se output_dir for fornecido, salva o consolidado_validado lá; caso contrário salva em ./consolidado_validado.
        """
        nomes_possiveis = ["consolidado_despesas.csv"]
        caminho_csv = None
        for nome in nomes_possiveis:
            p = os.path.join(input_dir, nome)
            if os.path.exists(p):
                caminho_csv = p
                break
        if caminho_csv is None:
            self.logger.error("Arquivo consolidado não encontrado na pasta de entrada: %s", input_dir)
            return None

        self.logger.info("Lendo arquivo consolidado: %s", caminho_csv)
        df = pd.read_csv(caminho_csv, sep=';', dtype=str, encoding='utf-8-sig', keep_default_na=False)

        # detectar nomes de coluna comuns
        cols = [c.lower() for c in df.columns]
        # CNPJ
        cnpj_coluna = None
        for c in df.columns:
            if 'cnpj' in c.lower():
                cnpj_coluna = c
                break
        if cnpj_coluna is None:
            self.logger.warning("Coluna CNPJ não encontrada; será criada vazia.")
            df['CNPJ'] = ""
            cnpj_coluna = 'CNPJ'

        # RAZAO SOCIAL
        razao_coluna = None
        for c in df.columns:
            coluna_minusculas = c.lower()
            if 'razao' in coluna_minusculas or 'razao_social' in coluna_minusculas or 'nome' in coluna_minusculas and 'fantasia' not in coluna_minusculas:
                razao_coluna = c
                break
        if razao_coluna is None:
            self.logger.warning("Coluna RazaoSocial não encontrada; será criada vazia.")
            df['RazaoSocial'] = ""
            razao_coluna = 'RazaoSocial'

        # VALOR (procura coluna provável)
        valor_coluna = None
        for c in df.columns:
            coluna_minusculas = c.lower()
            if any(procura in coluna_minusculas for procura in ('valor','vl_','vl ', 'vl', 'saldo','despesa','amount','quantia')):
                valor_coluna = c
                break
        if valor_coluna is None:
            self.logger.warning("Coluna de valor não identificada; será criada com zeros.")
            df['Valor'] = "0"
            valor_coluna = 'Valor'

        # aplicar validações
        self.logger.info("Executando validações (CNPJ, valor positivo, razão social não vazia)...")
        df['cnpj_normalizado'] = df[cnpj_coluna].apply(self.normalizar_cnpj)
        valid_cnpj = df[cnpj_coluna].apply(self.validar_cnpj)
        df['cnpj_valido'] = valid_cnpj.apply(lambda t: t[0])
        df['motivo_invalidez_cnpj'] = valid_cnpj.apply(lambda t: t[1])

        valid_valor = df[valor_coluna].apply(self.validar_valor_positivo)
        df['valor_positivo'] = valid_valor.apply(lambda t: t[0])
        df['motivo_valor'] = valid_valor.apply(lambda t: t[1])

        valid_razao = df[razao_coluna].apply(self.validar_razao_social)
        df['razao_social_nao_vazia'] = valid_razao.apply(lambda t: t[0])
        df['motivo_razao'] = valid_razao.apply(lambda t: t[1])

        # sumarizar
        total = len(df)
        cnpj_validos = int(df['cnpj_valido'].sum())
        valores_positivos = int(df['valor_positivo'].sum())
        razao_validas = int(df['razao_social_nao_vazia'].sum())
        self.logger.info("Total registros=%d; CNPJ válidos=%d; valores positivos=%d; razao social válidas=%d",
                         total, cnpj_validos, valores_positivos, razao_validas)

        # salvar uma cópia validada
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            out = os.path.join(output_dir, "consolidado_validado.csv")
        else:
            target_dir = os.path.join(os.path.dirname(__file__), "consolidado_validado")
            os.makedirs(target_dir, exist_ok=True)
            out = os.path.join(target_dir, "consolidado_validado.csv")

        try:
            df.to_csv(out, index=False, sep=';', encoding='utf-8-sig')
            self.logger.info("Arquivo validado salvo em: %s", out)
        except Exception as e:
            self.logger.warning("Falha ao salvar arquivo validado: %s", e)

        return df

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJETO_ROOT = os.path.dirname(SCRIPT_DIR)
    
    # Define a pasta raiz de dados (arquivos_csv_zips)
    PASTA_DADOS_RAIZ = os.path.join(PROJETO_ROOT, 'arquivos_csv_zips')
    
    # Define as pastas de entrada e saída
    pasta_entrada = os.path.join(PASTA_DADOS_RAIZ, "consolidado_despesas")
    pasta_saida = os.path.join(PASTA_DADOS_RAIZ, "consolidado_validado")
    
    val = ValidadorDados(logger=logger)
    df_resultado = val.validar_arquivo_consolidado(pasta_entrada, output_dir=pasta_saida)
    if df_resultado is not None:
        logger.info("Processamento finalizado; DataFrame com validações retornado.")
