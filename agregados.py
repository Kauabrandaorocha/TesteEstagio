# ...existing code...
import os
import logging
import pandas as pd
import zipfile

# Configuração de logging
logger = logging.getLogger("agregacao")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

# Ajuste seu nome aqui para o zip final: Teste_{NOME_AUTOR}.zip
NOME_AUTOR = "Kaua_Brandao"

def executar_agregacao():
    # raiz do projeto (src/agregar -> projeto root)
    projeto_root = os.path.dirname(os.path.abspath(__file__))
    # caminho do arquivo enriquecido dentro da pasta 
    caminho_enriquecido = os.path.join(projeto_root, "dados_enriquecidos", "dados_enriquecidos.csv")

    if not os.path.exists(caminho_enriquecido):
        logger.error("Arquivo enriquecido não encontrado: %s", caminho_enriquecido)
        return

    logger.info("Lendo arquivo enriquecido: %s", caminho_enriquecido)
    df = pd.read_csv(caminho_enriquecido, sep=';', dtype=str, encoding='utf-8-sig')

    # garantir colunas necessárias (criar com NaN se ausente)
    for col in ['RazaoSocial', 'UF', 'ValorDespesas', 'Ano', 'Trimestre']:
        if col not in df.columns:
            df[col] = pd.NA

    # converter ValorDespesas para numérico (coerce para NaN)
    df['ValorDespesas'] = pd.to_numeric(df['ValorDespesas'].astype(str).str.replace(",", "."), errors='coerce')

    # checar existência de dados válidos para RazaoSocial e UF
    n_valid_razao = df['RazaoSocial'].notna().sum()
    n_valid_uf = df['UF'].notna().sum()
    logger.info("Registros com RazaoSocial=%d, com UF=%d", int(n_valid_razao), int(n_valid_uf))

    # calcular total por RazaoSocial/UF (agrupa apenas onde chave existe)
    agrupado_total = (
        df.dropna(subset=['RazaoSocial', 'UF'])
          .groupby(['RazaoSocial', 'UF'], dropna=False)['ValorDespesas']
          .sum(min_count=1)
          .reset_index()
          .rename(columns={'ValorDespesas': 'TotalDespesas'})
    )

    # média trimestral: sumarizar por RazaoSocial/UF/Ano/Trimestre -> média dos totais trimestrais
    df_quarterly = (
        df.dropna(subset=['RazaoSocial', 'UF'])
          .groupby(['RazaoSocial', 'UF', 'Ano', 'Trimestre'], dropna=False)['ValorDespesas']
          .sum(min_count=1)
          .reset_index()
    )
    media_trimestral = (
        df_quarterly.groupby(['RazaoSocial', 'UF'], dropna=False)['ValorDespesas']
                   .mean()
                   .reset_index()
                   .rename(columns={'ValorDespesas': 'MediaTrimestral'})
    )

    # desvio padrão das despesas por RazaoSocial/UF
    desvio_padrao = (
        df.dropna(subset=['RazaoSocial', 'UF'])
          .groupby(['RazaoSocial', 'UF'], dropna=False)['ValorDespesas']
          .std(ddof=0)
          .reset_index()
          .rename(columns={'ValorDespesas': 'DesvioPadrao'})
    )

    # juntar métricas
    df_agregado = agrupado_total.merge(media_trimestral, on=['RazaoSocial', 'UF'], how='left') \
                                .merge(desvio_padrao, on=['RazaoSocial', 'UF'], how='left')

    # ordenar por TotalDespesas desc (NaN ao final)
    df_agregado = df_agregado.sort_values(by='TotalDespesas', ascending=False, na_position='last')

    # salvar dentro da pasta 'despesas_agregadas' conforme solicitado
    pasta_saida = os.path.join(projeto_root, "despesas_agregadas")
    os.makedirs(pasta_saida, exist_ok=True)
    caminho_saida_csv = os.path.join(pasta_saida, "despesas_agregadas.csv")

    df_agregado.to_csv(caminho_saida_csv, index=False, sep=';', encoding='utf-8-sig')
    logger.info("Arquivo de agregação salvo em: %s (linhas=%d)", caminho_saida_csv, len(df_agregado))

    # compactar em zip na mesma pasta
    caminho_zip = os.path.join(pasta_saida, f"Teste_{NOME_AUTOR}.zip")
    with zipfile.ZipFile(caminho_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(caminho_saida_csv, arcname=os.path.basename(caminho_saida_csv))
    logger.info("Compactado em: %s", caminho_zip)

if __name__ == "__main__":
    executar_agregacao()
