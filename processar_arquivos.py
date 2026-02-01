import pandas as pd
import os
import logging

def processar_formatos_diferentes(caminho, colunas, chunk_size):
    extensao = os.path.splitext(caminho)[1].lower()

    if extensao in ['.csv', '.txt']:
        for sep in [';', ',', '\t']:
            return pd.read_csv(caminho, sep=sep, usecols=colunas, chunksize=chunk_size, encoding='utf-8')
    elif extensao in ['.xlsx', '.xls']:
        df_full = pd.read_excel(caminho, usecols=colunas)
        return [df_full]

    else:
        return logging.error("Formato de arquivo não suportado")



arquivos = ["1T2025.csv", "2T2025.csv", "3T2025.csv"] # declara os arquivos aqui
df_list = []

# percorre cada arquivo para processar os dados
for arquivo in arquivos:
    caminho_csv = os.path.join("arquivos_extraidos", arquivo) # define o caminho
    dataframe = pd.read_csv(caminho_csv, sep=';', usecols=['DESCRICAO'], chunksize=chunk_incremental) # leitura dos arquivos .csv

    """
    DEBUG PARA SABER SE O INCREMENTO ESTÁ FUNCIONANDO, COM BASE NO CHUNK DEFINIDO ACIMA

    for i, pedaco in enumerate(dataframe):
        print(f"Lendo pedaço {i} do arquivo {arquivo}...") 
        df_list.append(pedaco)
    """

    # para leitura correta dos chunks, necessário percorrer toda a coluna
    for chunk in dataframe:
        # normalizar para minúsculas
        chunk.columns = chunk.columns.str.lower()

        # remover espaços em branco
        chunk['descricao'] = chunk['descricao'].str.strip()

        # aplicar filtro com regex, buscando o dado especifico
        filtro = chunk['descricao'].str.contains(r"despesas?\s+com\s+(?:eventos?|sinistros?)", case=False, na=False)

        # adiciona a lista
        df_list.append(chunk[filtro])

# concatena todas as partes filtradas contendo só os dados com despesas com eventos/sinistros
df_final = pd.concat(df_list, ignore_index=True)

# debug
print(df_final)
