import pandas as pd
import os
import logging
import glob
import zipfile

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


def executar_processamento():
    # acessa o diretório principal onde estão os arquivos extraídos. ex: C:/Users/SeuUsuario/caminho/da/pasta/arquivos_extraidos
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # concatena o diretório base com a pasta dos arquivos extraídos
    DF_DIR = os.path.join(BASE_DIR, "arquivos_extraidos")

    if not os.path.exists(DF_DIR):
        logging.error(f"O diretório {DF_DIR} não existe.")
        return
    
    colunas = [
        'DATA',
        'REG_ANS',
        'CD_CONTA_CONTABIL',
        'DESCRICAO',
        'VL_SALDO_INICIAL',
        'VL_SALDO_FINAL'
    ]
    df_list = []

    # tranforma em lista e percorre os arquivos do diretório onde estão os arquivos extraídos
    for nome_arquivo in sorted(os.listdir(DF_DIR)):
        # verifica se o arquivo possui uma das extensões suportadas
        if nome_arquivo.endswith(('.csv', '.txt', '.xlsx', '.xls')):
            caminho = os.path.join(DF_DIR, nome_arquivo)
            dataframe = processar_formatos_diferentes(caminho, colunas, chunk_size=30000)

            if dataframe is None:
                logging.error(f"Não foi possível processar o arquivo: {caminho}")
                continue

            """
            DEBUG PARA SABER SE O INCREMENTO ESTÁ FUNCIONANDO, COM BASE NO CHUNK DEFINIDO ACIMA

            for i, pedaco in enumerate(dataframe):
                print(f"Lendo pedaço {i} do arquivo {nome_arquivo}...") 
                df_list.append(pedaco)
            """
            # para leitura correta dos chunks, necessário percorrer todas as coluna
            for chunk in dataframe:
                # normalizar todas as colunas para minúsculas
                chunk.columns = chunk.columns.str.lower()

                # remover espaços em branco
                chunk['descricao'] = chunk['descricao'].astype(str).str.strip()

                # aplicar filtro com regex, buscando o dado especifico
                filtro = chunk['descricao'].str.contains(r"despesas?\s+com\s+(?:eventos?|sinistros?)", case=False, na=False)

                # adiciona a lista
                df_list.append(chunk[filtro])

            if df_list:
                # concatena todas as partes filtradas contendo só os dados com despesas com eventos/sinistros
                df_final = pd.concat(df_list, ignore_index=True)

                df_final["data"] = pd.to_datetime(df_final["data"], errors="coerce")
                # pega a parte do ano da coluna 'data'
                df_final["ano"] = df_final["data"].dt.year
                # pega a parte do trimestre da coluna 'data'
                df_final["trimestre"] = df_final["data"].dt.quarter

                # transforma os valores para númericos e subtitui a virgula para ponto, evitando erros indevidos ao formato brasileiro
                saldo_inicial = pd.to_numeric(df_final["vl_saldo_inicial"].astype(str).str.replace(",", "."), errors="coerce")
                saldo_final = pd.to_numeric(df_final["vl_saldo_final"].astype(str).str.replace(",", "."), errors="coerce")
                df_final["valor_despesas"] = abs(saldo_final - saldo_inicial).round(2)

                df_final["cnpj"] = pd.NA
                df_final["razao_social"] = pd.NA

                df_consolidado = pd.DataFrame({
                    "CNPJ": df_final.get("cnpj"),
                    "RazaoSocial": df_final.get("razao_social"),
                    "Ano": df_final["ano"],
                    "Trimestre": df_final["trimestre"],
                    "ValorDespesas": df_final["valor_despesas"]
                })

                # define o caminho so arquivo csv consolidado(so com os dados filtrados de despesas com eventos/sinistros)
                CONSOLIDADO_DIR = os.path.join(BASE_DIR, "consolidado_despesas")
                caminho_csv = os.path.join(CONSOLIDADO_DIR, "consolidado_despesas.csv")
                
                # transforma em csv
                df_consolidado.to_csv(caminho_csv, index=False, encoding="utf-8-sig", sep=";")

                # compacta o arquivo csv em um zip  
                caminho_zip = os.path.join(CONSOLIDADO_DIR, "consolidado_despesas.zip")

                with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zip:
                    zip.write(caminho_csv)

                # debug
                print(df_consolidado)
            else:
                logging.info(f"Nenhum dado correspondente encontrado no arquivo: {caminho}")

# é utilizado para garantir que o código seja executado quando executar o script(pelo terminal ou IDE), mas não quando for importado como módulo em outro script
if __name__ == "__main__":
    executar_processamento()
