import pandas as pd
import os
import logging
import zipfile

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def processar_formatos_diferentes(caminho, colunas, chunk_size):
    extensao = os.path.splitext(caminho)[1].lower()
    try:
        if extensao in ['.csv', '.txt']:
            for sep in [';', ',', '\t']:
                try:   
                    df = pd.read_csv(caminho, sep=sep, nrows=0, encoding='latin1')
                    cols_no_arquivo = [c.upper().strip() for c in df.columns]
                    cols_desejadas = [c.upper().strip() for c in colunas]

                    if all(c in cols_no_arquivo for c in cols_desejadas):
                        return pd.read_csv(caminho, sep=sep, usecols=colunas, chunksize=chunk_size, encoding='latin1')
                except:
                    continue
            
            return pd.read_csv(caminho, sep=';', names=colunas, chunksize=chunk_size, encoding='latin1', header=None)
        elif extensao in ['.xlsx', '.xls']:
            df_full = pd.read_excel(caminho, usecols=colunas)
            return [df_full]
    except Exception as e:
        logging.error(f"Erro ao processar o arquivo {caminho}: {e}")

def executar_processamento():
    # --- MAPEAMENTO DE DIRETÓRIOS ---
    # 1. Localiza a pasta onde este script está (scripts_python)
    BASE_SCRIPTS = os.path.dirname(os.path.abspath(__file__))

    # 2. Sobe UM nível para a raiz do projeto (onde estão as outras pastas)
    PROJETO_ROOT = os.path.dirname(BASE_SCRIPTS)

    # 3. Define o caminho para a pasta principal de arquivos
    RAIZ_DADOS = os.path.join(PROJETO_ROOT, 'arquivos_csv_zips')

    # 4. Define as subpastas dentro da pasta de dados
    DF_DIR = os.path.join(RAIZ_DADOS, "arquivos_extraidos")
    CADASTRO_DIR = os.path.join(RAIZ_DADOS, "dados_cadastrais")
    CONSOLIDADO_DIR = os.path.join(RAIZ_DADOS, "consolidado_despesas")

    if not os.path.exists(DF_DIR):
        logging.error(f"O diretório {DF_DIR} não existe.")
        return

    os.makedirs(CONSOLIDADO_DIR, exist_ok=True)
    
    colunas = ['DATA', 'REG_ANS', 'CD_CONTA_CONTABIL', 'DESCRICAO', 'VL_SALDO_INICIAL', 'VL_SALDO_FINAL']
    df_list = []

    # 1. Processamento dos arquivos de despesas
    for nome_arquivo in sorted(os.listdir(DF_DIR)):
        if nome_arquivo.endswith(('.csv', '.txt', '.xlsx', '.xls')):
            caminho = os.path.join(DF_DIR, nome_arquivo)
            dataframe = processar_formatos_diferentes(caminho, colunas, chunk_size=30000)

            if dataframe is not None:
                for chunk in dataframe:
                    chunk.columns = chunk.columns.str.lower()
                    chunk['descricao'] = chunk['descricao'].astype(str).str.strip()
                    filtro = chunk['descricao'].str.contains(r"despesas?\s+com\s+(?:eventos?|sinistros?)", case=False, na=False)
                    df_list.append(chunk[filtro])

    if df_list:
        df_final = pd.concat(df_list, ignore_index=True)

        # 2. Carregamento do Cadastro (Ponte)
        try:
            caminho_cad = os.path.join(CADASTRO_DIR, "Relatorio_cadop.csv")
            df_cadastral = pd.read_csv(caminho_cad, sep=';', encoding='latin1', dtype=str)
            df_cadastral.columns = [c.strip().upper() for c in df_cadastral.columns]
            
            mapa_cnpj = df_cadastral.set_index('REGISTRO_OPERADORA')['CNPJ'].to_dict()
            mapa_razao = df_cadastral.set_index('REGISTRO_OPERADORA')['RAZAO_SOCIAL'].to_dict()
        except Exception as e:
            logging.error(f"Erro ao carregar cadastro em {caminho_cad}: {e}")
            return

        # 3. Tratamento de dados
        df_final["data"] = pd.to_datetime(df_final["data"], errors="coerce")
        df_final["ano"] = df_final["data"].dt.year
        df_final["trimestre"] = df_final["data"].dt.quarter
        
        saldo_ini = pd.to_numeric(df_final["vl_saldo_inicial"].astype(str).str.replace(",", "."), errors="coerce")
        saldo_fim = pd.to_numeric(df_final["vl_saldo_final"].astype(str).str.replace(",", "."), errors="coerce")
        df_final["valor_despesas"] = abs(saldo_fim - saldo_ini).round(2)

        df_final['reg_ans_str'] = df_final['reg_ans'].astype(str).str.replace('.0', '', regex=False).str.strip()
        df_final["cnpj"] = df_final["reg_ans_str"].map(mapa_cnpj)
        df_final["razao_social"] = df_final["reg_ans_str"].map(mapa_razao)

        # 4. Exportação
        df_consolidado = pd.DataFrame({
            "CNPJ": df_final["cnpj"],
            "RazaoSocial": df_final["razao_social"],
            "Ano": df_final["ano"],
            "Trimestre": df_final["trimestre"],
            "ValorDespesas": df_final["valor_despesas"]
        })

        caminho_csv = os.path.join(CONSOLIDADO_DIR, "consolidado_despesas.csv")
        df_consolidado.to_csv(caminho_csv, index=False, encoding="utf-8-sig", sep=";")

        caminho_zip = os.path.join(CONSOLIDADO_DIR, "consolidado_despesas.zip")
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # zipf.write(caminho_csv, arcname="consolidado_despesas.csv")
            zipf.write(caminho_csv, os.path.basename(caminho_csv))

        logging.info(f"Sucesso! Arquivo consolidado gerado em: {CONSOLIDADO_DIR}")
    else:
        logging.warning("Nenhum dado filtrado encontrado para consolidar.")

if __name__ == "__main__":
    executar_processamento()