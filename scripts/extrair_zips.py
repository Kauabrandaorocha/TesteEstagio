import zipfile
import os
import logging

def extrair_arquivos_zip():
    # 1. Localiza a pasta onde o script está (scripts_python)
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Sobe UM nível para a raiz do projeto
    PROJETO_ROOT = os.path.dirname(SCRIPT_DIR)
    
    # 3. Define a pasta principal de dados
    PASTA_DADOS = os.path.join(PROJETO_ROOT, 'arquivos_csv_zips')
    
    # --- SOLUÇÃO 1: Garantir que TODAS as pastas do fluxo existam ---
    pastas_necessarias = [         # Onde ficam os ZIPs da ANS
        'arquivos_extraidos',    # Onde os CSVs crus serão jogados
        'consolidado_despesas',  # Resultado do processamento
        'consolidado_validado',  # Resultado da validação
        'dados_enriquecidos',    # Resultado do enriquecimento
        'despesas_agregadas'     # Resultado final (Agregação + ZIP final)
    ]
    
    for subpasta in pastas_necessarias:
        caminho_completo_pasta = os.path.join(PASTA_DADOS, subpasta)
        if not os.path.exists(caminho_completo_pasta):
            print(f"Criando pasta: {subpasta}")
            os.makedirs(caminho_completo_pasta, exist_ok=True)

    # 4. Caminho específico dos zips para extração
    CAMINHO_ZIP = os.path.join(PASTA_DADOS, 'arquivoszip')
    PASTA_EXTRAIDOS = os.path.join(PASTA_DADOS, 'arquivos_extraidos')
    
    # Verifica se há algo para extrair
    if not os.path.exists(CAMINHO_ZIP) or not os.listdir(CAMINHO_ZIP):
        print(f"Atenção: Coloque os arquivos .zip em {CAMINHO_ZIP} para continuar.")
        return

    arquivos = os.listdir(CAMINHO_ZIP)

    for arquivo in arquivos:
        if arquivo.endswith(".zip"):
            caminho_completo = os.path.join(CAMINHO_ZIP, arquivo)
            
            try:
                with zipfile.ZipFile(caminho_completo, 'r') as zip_ref:
                    print(f"Extraindo {arquivo} para {PASTA_EXTRAIDOS}...")
                    zip_ref.extractall(PASTA_EXTRAIDOS)
            except zipfile.BadZipFile:
                logging.error(f"Arquivo Zip corrompido: {caminho_completo}")

if __name__ == "__main__":
    extrair_arquivos_zip()


"""
        # todo esse comando serve para criar pastas com o mesmo nome do zip para evitar duplicações em uma situação de grande volume de arquivos por zip
        nome_zip = os.path.splitext(arquivo)[0] # obtém o nome do arquivo sem a extensão .zip
        caminho_extraido = os.path.join("arquivos_extraidos/", nome_zip) # cria o caminho para a pasta onde os arquivos serão extraídos

        os.makedirs(caminho_extraido, exist_ok=True) # cria pasta recursivamente e o exist_ok evita erro se ja existir 
        """