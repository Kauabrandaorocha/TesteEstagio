# executar a extração dos arquivos: python extrair_zips.py
import zipfile
import os
import logging

def extrair_arquivos_zip(caminho_pasta):
    caminho_zip = caminho_pasta # acessa a pasta
    arquivos = os.listdir(caminho_zip) # retorna uma lista de todos os arquivos presentes na pasta)

    # percorre a lista e verifica se algum arquivo tem a terminação .zip
    for arquivo in arquivos:
        if arquivo.endswith(".zip"):
            caminho_completo = os.path.join(caminho_zip, arquivo) # une o caminho da pasta com o nome dos arquivos
        
            try:
                with zipfile.ZipFile(caminho_completo, 'r') as zip:
                    # debugg
                    print(f"Extraindo arquivo: {arquivo}")
                    zip.extractall("arquivos_extraidos/") # colocar nome qualquer para a pasta que contem os arquivos extraidos

            except zipfile.BadZipFile:
                logging.error(f"Arquivo Zip corrompido/inválido: {caminho_completo}")
        
        """
        # todo esse comando serve para criar pastas com o mesmo nome do zip para evitar duplicações em uma situação de grande volume de arquivos por zip
        nome_zip = os.path.splitext(arquivo)[0] # obtém o nome do arquivo sem a extensão .zip
        caminho_extraido = os.path.join("arquivos_extraidos/", nome_zip) # cria o caminho para a pasta onde os arquivos serão extraídos

        os.makedirs(caminho_extraido, exist_ok=True) # cria pasta recursivamente e o exist_ok evita erro se ja existir 
        """
        
extrair_arquivos_zip("arquivoszip/")


