import pandas as pd
import os
import logging
import glob

# configura logging para aparecer no terminal e realizar debugs
logging.basicConfig(
    level=logging.DEBUG, # Pode ser DEBUG, INFO, WARNING, ERROR, CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def processar_formatos_diferentes(caminho, colunas, chunk_size):
    extensao = os.path.splitext(caminho)[1].lower() # trasnforma o caminho em uma tupla contendo o nome e o caminho do arquivo, e sua extensão
    try:
        # verifica qual tipo de extensao o arquivo possui
        if extensao in ['.csv', '.txt']:
            # verifica se os arquivos possuem os tipos de separadores
            for sep in [';', ',', '\t']:
                try:   
                    # le normalmente o arquivo para verificar se as colunas existem
                    df = pd.read_csv(caminho, sep=sep, nrows=0, encoding='latin1')
                    
                    # percorre as colunas presentes no dataframe lido
                    cols_no_arquivo = [c.upper().strip() for c in df.columns]
                    # percorre as colunas colocadas no parametro da função
                    cols_desejadas = [c.upper().strip() for c in colunas]

                    # verifica se todas as colunas atribuidas pelo parametro da função estão presentes nas colunas dos arquivos, retornando True(função all) se sim.
                    if all(c in cols_no_arquivo for c in cols_desejadas):
                        # ve se as colunas existem
                        return pd.read_csv(caminho, sep=sep, usecols=colunas, chunksize=chunk_size, encoding='latin1')

                    else:
                        logging.info(f"Colunas não encontradas no arquivo: {caminho} com separador '{sep}'.")

                except:
                    continue
            
            logging.info(f"Cabeçalho não identificado em {caminho}. Atribuindo manualmente com ';'.")
            return pd.read_csv(caminho, sep=';', names=colunas, chunksize=chunk_size, encoding='latin1', header=None)

        elif extensao in ['.xlsx', '.xls']:
            df_full = pd.read_excel(caminho, usecols=colunas)
            return [df_full]

        else:
            return logging.error("Formato de arquivo não suportado")

        
    except Exception as e:
        logging.error(f"Erro ao processar o arquivo {caminho}: {e}")



arquivos = ["1T2025.csv", "2T2025.csv", "3T2025.csv"] # declara os arquivos aqui
colunas = [
    'DATA',
    'REG_ANS',
    'CD_CONTA_CONTABIL',
    'DESCRICAO',
    'VL_SALDO_INICIAL',
    'VL_SALDO_FINAL'
] # define as colunas que serão lidas
df_list = []

# percorre cada arquivo para processar os dados
for nome_arquivo in arquivos:
    caminho = os.path.join("arquivos_extraidos", nome_arquivo) # define o caminho
    dataframe = processar_formatos_diferentes(caminho, colunas, chunk_size=100000)# leitura dos arquivos .csv/.txt/.xlsx/.xls em chunks de 100.000 linhas

    if dataframe is None:
        logging.error(f"Não foi possível processar o arquivo: {caminho}")
        continue

    """
    DEBUG PARA SABER SE O INCREMENTO ESTÁ FUNCIONANDO, COM BASE NO CHUNK DEFINIDO ACIMA

    for i, pedaco in enumerate(dataframe):
        print(f"Lendo pedaço {i} do arquivo {arquivo}...") 
        df_list.append(pedaco)
    """

    # para leitura correta dos chunks, necessário percorrer todas as coluna
    for chunk in dataframe:
        # normalizar para minúsculas
        chunk.columns = chunk.columns.str.lower()

        # remover espaços em branco
        chunk['descricao'] = chunk['descricao'].astype(str).str.strip()

        # aplicar filtro com regex, buscando o dado especifico
        filtro = chunk['descricao'].str.contains(r"despesas?\s+com\s+(?:eventos?|sinistros?)", case=False, na=False)

        # adiciona a lista
        df_list.append(chunk[filtro])

# concatena todas as partes filtradas contendo só os dados com despesas com eventos/sinistros
df_final = pd.concat(df_list, ignore_index=True)

pegar_arquivos = glob.glob("arquivos_extraidos/*.csv")
csv_consolidado = pd.concat([pd.read_csv(f) for f in pegar_arquivos])
csv_consolidado.to_csv("consolidado.csv", index=False, encoding='latin1')

# debug
print(df_final)
