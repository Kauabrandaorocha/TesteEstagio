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
                zip.extractall("caminho_zip")
except zipfile.BadZipFile:
    logging.error(f"Arquivo(s) Zip corrompidos/inválidos.")

