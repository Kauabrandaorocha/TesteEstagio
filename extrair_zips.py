# executar a extração dos arquivos: python extrair_zips.py
import zipfile
import os
import logging

try:
    # acessa a pasta
    caminho_zip = "arquivoszip/"

    # retorna uma lista de todos os arquivos presentes na pasta
    arquivos = os.listdir(caminho_zip)

    # percorre a lista e verifica se algum arquivo tem a terminação .zip para poder unir o caminho da pasta com o nome dos arquivos
    for arquivo in arquivos:
        if arquivo.endswith(".zip"):
            caminho_completo_arquivo =  os.path.join(caminho_zip, arquivo)
            
            # utilizar leitura para descompactar os arquivos .zip
            with zipfile.ZipFile(caminho_completo_arquivo, 'r') as zip:
                # debugg: print(f"Extraindo arquivo: {arquivo}")
                zip.extractall("arquivos_extraidos/") # colocar nome qualquer para a pasta que contem os arquivos extraidos

except zipfile.BadZipFile:
    logging.error(f"Arquivo(s) Zip corrompidos/inválidos.")

