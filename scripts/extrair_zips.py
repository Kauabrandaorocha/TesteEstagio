import zipfile
import os
import logging

def extrair_arquivos_zip():
    # 1. Localiza a pasta onde o script está (scripts_python)
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Sobe UM nível para a raiz do projeto
    PROJETO_ROOT = os.path.dirname(SCRIPT_DIR)
    
    # 3. Define os caminhos exatos na pasta de arquivos
    # Note: verifique se o nome é 'arquivos_csv_zip' ou 'arquivos_csv_zips'
    PASTA_DADOS = os.path.join(PROJETO_ROOT, 'arquivos_csv_zips')
    CAMINHO_ZIP = os.path.join(PASTA_DADOS, 'arquivoszip')
    PASTA_EXTRAIDOS = os.path.join(PASTA_DADOS, 'arquivos_extraidos')
    
    # Validação para não criar pastas erradas
    if not os.path.exists(CAMINHO_ZIP):
        print(f"Erro: A pasta de origem {CAMINHO_ZIP} não existe.")
        return

    # Garante que a pasta de destino existe (não cria pastas extras no caminho)
    os.makedirs(PASTA_EXTRAIDOS, exist_ok=True)
    
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