# ...existing code...
import os
import re
import logging
import pandas as pd

# Configuração de logging (simples e legível)
logger_enriquecimento = logging.getLogger("enriquecimento_dados")
logger_enriquecimento.setLevel(logging.INFO)
_stream_handler = logging.StreamHandler()
_stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger_enriquecimento.addHandler(_stream_handler)


def normalizar_cnpj(valor):
    """Remove caracteres não numéricos; retorna string vazia se ausente."""
    if pd.isna(valor):
        return ""
    return re.sub(r"\D", "", str(valor))

# normalizar_cnpj: usado para remover pontuação e deixar apenas dígitos
# Isso facilita o join entre arquivos onde o CNPJ pode vir formatado de formas diferentes


def ler_csv_com_delimitadores_possiveis(caminho_arquivo):
    """Tenta ler CSV com ';' e faz fallback para ',' se necessário."""
    try:
        return pd.read_csv(caminho_arquivo, sep=';', dtype=str, encoding='utf-8-sig')

    except Exception:
        return pd.read_csv(caminho_arquivo, sep=',', dtype=str, encoding='utf-8-sig')

# ler_csv_com_delimitadores_possiveis: tenta primeiro ler com ponto-e-vírgula (padrão BR),
# se der erro tenta com vírgula. Evita falhas quando o arquivo tem delimitador diferente.


def encontrar_coluna(df, nomes_possiveis):
    """Retorna o primeiro nome presente em df a partir da lista nomes_possiveis."""
    for nome in nomes_possiveis:
        if nome in df.columns:
            return nome
    return None

# encontrar_coluna: utilitário para detectar colunas com nomes variados entre arquivos
# ex: 'RegistroANS' pode aparecer como 'REG_ANS' ou 'registro_ans'


def agregar_valores_unicos_com_join(grupo, nome_coluna):
    """Retorna string com valores únicos (ordenados) separados por ' | ' ou pd.NA."""
    if nome_coluna is None:
        return pd.NA
    valores = sorted({str(x).strip() for x in grupo[nome_coluna].fillna("") if str(x).strip()})

    return " | ".join(valores) if valores else pd.NA

# agregar_valores_unicos_com_join: quando o cadastro tem múltiplas linhas por CNPJ,
# concatena todas as variações (sem duplicatas) em uma string para auditoria.


def escolher_valor_principal(grupo, nome_coluna):
    """Escolhe o valor principal do grupo: o mais frequente não vazio, ou pd.NA."""
    if nome_coluna is None:
        return pd.NA

    serie = grupo[nome_coluna].fillna("").astype(str).str.strip()
    serie = serie[serie != ""]

    if serie.empty:
        return pd.NA
    return serie.value_counts().idxmax()

# escolher_valor_principal: quando há múltiplas entradas diferentes para o mesmo CNPJ,
# escolhemos a opção mais frequente como registro 'principal' — estratégia simples e
# interpretável. Pode ser substituída por lógica mais avançada (e.g., data mais recente).


def enriquecer_por_cadastro(diretorio_consolidado, diretorio_cadastro):
    """
    LEFT JOIN entre consolidado e cadastro.
    Produz dados_enriquecidos.csv em pasta dados_enriquecidos e um arquivo de conflitos cadastro_conflitos.csv.
    Colunas finais em dados_enriquecidos.csv:
      CNPJ, RazaoSocial, Ano, Trimestre, ValorDespesas, RegistroANS, Modalidade, UF, ConflitoCadastro
    """
    # localizar consolidado
    nomes_consolidados = ["consolidado_despesas.csv", "consolidado_despesas_validado.csv", "consolidado.csv"]
    caminho_consolidado = None

    for nome in nomes_consolidados:
        candidato = os.path.join(diretorio_consolidado, nome)
        if os.path.exists(candidato):
            caminho_consolidado = candidato
            break

    if caminho_consolidado is None:
        logger_enriquecimento.error("Arquivo consolidado não encontrado em: %s", diretorio_consolidado)
        return None

    # localizar cadastro
    caminho_cadastro = os.path.join(diretorio_cadastro, "Relatorio_cadop.csv")
    if not os.path.exists(caminho_cadastro):
        lista_csv = [f for f in os.listdir(diretorio_cadastro) if f.lower().endswith('.csv')]

        if not lista_csv:
            logger_enriquecimento.error("Arquivo de cadastro não encontrado em: %s", diretorio_cadastro)
            return None

        caminho_cadastro = os.path.join(diretorio_cadastro, lista_csv[0])
        logger_enriquecimento.warning("Usando primeiro CSV encontrado em dados_cadastrais: %s", lista_csv[0])

    logger_enriquecimento.info("Lendo consolidado: %s", caminho_consolidado)

    df_consolidado = ler_csv_com_delimitadores_possiveis(caminho_consolidado)

    logger_enriquecimento.info("Lendo cadastro: %s", caminho_cadastro)

    df_cadastro = ler_csv_com_delimitadores_possiveis(caminho_cadastro)

    # garantir coluna CNPJ no consolidado
    if 'CNPJ' not in df_consolidado.columns:
        logger_enriquecimento.warning("Coluna 'CNPJ' não encontrada no consolidado; criando vazia.")
        df_consolidado['CNPJ'] = ""

    # identificar coluna CNPJ no cadastro
    coluna_cnpj_cadastro = encontrar_coluna(df_cadastro, ['CNPJ', 'CNPJ_CPF', 'cpf_cnpj', 'cnpj_cadastro', 'documento'])

    if coluna_cnpj_cadastro is None:
        coluna_cnpj_cadastro = df_cadastro.columns[0]
        logger_enriquecimento.warning("Coluna CNPJ no cadastro não claramente identificada; usando '%s'.", coluna_cnpj_cadastro)

    # normalizar CNPJ para join
    df_consolidado['cnpj_normalizado'] = df_consolidado['CNPJ'].apply(normalizar_cnpj)
    df_cadastro['cnpj_normalizado'] = df_cadastro[coluna_cnpj_cadastro].apply(normalizar_cnpj)

    coluna_registro_ans = encontrar_coluna(df_cadastro, ['REGISTRO_OPERADORA', 'RegistroANS', 'registro_ans', 'REG_ANS'])
    coluna_modalidade = encontrar_coluna(df_cadastro, ['MODALIDADE', 'Modalidade', 'modalidade'])
    coluna_uf = encontrar_coluna(df_cadastro, ['UF', 'uf', 'Uf'])
    coluna_razao_social = encontrar_coluna(df_cadastro, ['RAZAO_SOCIAL', 'RazaoSocial', 'razao_social', 'nome'])

    # identificar colunas no cadastro
    coluna_registro_ans = encontrar_coluna(df_cadastro, ['RegistroANS', 'registro_ans', 'REG_ANS', 'registro'])

    coluna_modalidade = encontrar_coluna(df_cadastro, ['Modalidade', 'modalidade', 'MODALIDADE'])

    coluna_uf = encontrar_coluna(df_cadastro, ['UF', 'uf', 'Uf'])

    coluna_razao_social = encontrar_coluna(df_cadastro, ['RazaoSocial', 'razao_social', 'RAZAO_SOCIAL', 'nome', 'nome_fantasia', 'Razao'])

    # agregar por cnpj_normalizado determinando valor principal e coletando variações
    registros_aggregados = []
    conflitos_lista = []
    contador_duplicados = 0
    contador_conflitos = 0

    grouped = df_cadastro.groupby('cnpj_normalizado', dropna=False)
    for cnpj_val, grupo in grouped:
        is_duplicado = len(grupo) > 1
        if is_duplicado:
            contador_duplicados += 1

        # valores agregados (todas as variações)
        registro_ans_all = agregar_valores_unicos_com_join(grupo, coluna_registro_ans)

        modalidade_all = agregar_valores_unicos_com_join(grupo, coluna_modalidade)

        uf_all = agregar_valores_unicos_com_join(grupo, coluna_uf)

        razao_social_all = agregar_valores_unicos_com_join(grupo, coluna_razao_social)

        # valor principal escolhido (mais frequente)
        registro_ans_principal = escolher_valor_principal(grupo, coluna_registro_ans)

        modalidade_principal = escolher_valor_principal(grupo, coluna_modalidade)

        uf_principal = escolher_valor_principal(grupo, coluna_uf)

        razao_social_principal = escolher_valor_principal(grupo, coluna_razao_social)

        # detectar conflito: mesma CNPJ com valores diferentes em campos relevantes
        # lógica: se a string agregada contiver mais de um valor distinto (separados por ' | ')
        # então há variação naquele campo e marcamos como conflito
        conflito = any(
            len([v for v in vals.split(" | ") if v]) > 1
            for vals in (registro_ans_all, modalidade_all, uf_all, razao_social_all)
            if pd.notna(vals)
        )


        if conflito:
            contador_conflitos += 1
            conflitos_lista.append({
                'cnpj_normalizado': cnpj_val,
                'RegistroANS_variacoes': registro_ans_all,
                'Modalidade_variacoes': modalidade_all,
                'UF_variacoes': uf_all,
                'RazaoSocial_variacoes': razao_social_all,
                'registro_principal': registro_ans_principal,
                'modalidade_principal': modalidade_principal,
                'uf_principal': uf_principal,
                'razao_principal': razao_social_principal,
                'total_linhas_no_cadastro': len(grupo)
            })


        registros_aggregados.append({
            'cnpj_normalizado': cnpj_val,
            'RegistroANS': registro_ans_principal,
            'Modalidade': modalidade_principal,
            'UF': uf_principal,
            'RazaoSocial': razao_social_principal,
            'cadastro_duplicado': is_duplicado,
            'conflito_cadastro': bool(conflito)
        })

    # 1. Transforma a lista do loop em DataFrame
    df_cadastro_agg = pd.DataFrame(registros_aggregados)

    # 2. GARANTIA ABSOLUTA: Remove qualquer duplicata de CNPJ que tenha sobrado no cadastro
    df_cadastro_agg = df_cadastro_agg.drop_duplicates(subset=['cnpj_normalizado'])

    # 3. Faz o merge
    df_enriquecido = df_consolidado.merge(df_cadastro_agg, on='cnpj_normalizado', how='left')

    # 4. CHECAGEM DE SEGURANÇA (Adicione isso para ver no terminal)
    if len(df_enriquecido) > len(df_consolidado):
        logger_enriquecimento.warning("ALERTA: O merge duplicou linhas! Ajustando...")
        # Se o merge duplicou, é porque o consolidado tinha CNPJs repetidos que não deveriam estar lá
        # ou o merge encontrou chaves extras. Vamos manter apenas o que importa.

# LEFT JOIN: uso intencional para preservar todas as linhas do consolidado mesmo
# quando não houver correspondência no cadastro; colunas do cadastro virão como NaN.

    # garantir Ano/Trimestre (usar colunas existentes ou inferir de 'data' com quarter)
    coluna_ano_existente = encontrar_coluna(df_enriquecido, ['Ano', 'ano', 'ANO'])

    coluna_trimestre_existente = encontrar_coluna(df_enriquecido, ['Trimestre', 'trimestre', 'TRIMESTRE'])

    if coluna_ano_existente and coluna_trimestre_existente:
        df_enriquecido['Ano'] = df_enriquecido[coluna_ano_existente]

        df_enriquecido['Trimestre'] = df_enriquecido[coluna_trimestre_existente]

    else:
        coluna_data = encontrar_coluna(df_enriquecido, ['data', 'DATA', 'Data'])
        if coluna_data:
            dt = pd.to_datetime(df_enriquecido[coluna_data], dayfirst=True, errors='coerce')
            df_enriquecido['Ano'] = dt.dt.year

            # dt.dt.quarter converte o mês em trimestre automaticamente (1..4)
            df_enriquecido['Trimestre'] = dt.dt.quarter
        else:
            df_enriquecido['Ano'] = pd.NA
            df_enriquecido['Trimestre'] = pd.NA

    # ValorDespesas: preferir coluna existente; senão calcular abs(final - inicial)
    coluna_valor_existente = encontrar_coluna(df_enriquecido, ['ValorDespesas', 'valor_despesas', 'VALOR_DESPESAS'])
    if coluna_valor_existente:
        df_enriquecido['ValorDespesas'] = pd.to_numeric(df_enriquecido[coluna_valor_existente], errors='coerce')

    else:
        coluna_vl_inicial = encontrar_coluna(df_enriquecido, ['VL_SALDO_INICIAL', 'vl_saldo_inicial', 'vl_saldo_inicio', 'vl_saldo'])

        coluna_vl_final = encontrar_coluna(df_enriquecido, ['VL_SALDO_FINAL', 'vl_saldo_final', 'vl_saldo_fim'])

        serie_inicial = pd.to_numeric(df_enriquecido.get(coluna_vl_inicial), errors='coerce') if coluna_vl_inicial else pd.Series([pd.NA] * len(df_enriquecido))

        serie_final = pd.to_numeric(df_enriquecido.get(coluna_vl_final), errors='coerce') if coluna_vl_final else pd.Series([pd.NA] * len(df_enriquecido))

        # calcula diferença absoluta entre saldo final e inicial como valor de despesa
        df_enriquecido['ValorDespesas'] = (serie_final - serie_inicial).abs()

    # garantir colunas necessárias antes de selecionar (evita KeyError)
    for coluna_necessaria in ['RegistroANS', 'Modalidade', 'UF', 'conflito_cadastro']:
        if coluna_necessaria not in df_enriquecido.columns:
            df_enriquecido[coluna_necessaria] = pd.NA

    # garantir que ConflitoCadastro seja booleano (True/False) — preencher NaN com False
    # isso facilita filtros e relatórios downstream (evita valores nulos)
    df_enriquecido['conflito_cadastro'] = df_enriquecido['conflito_cadastro'].fillna(False).astype(bool)

    if 'RazaoSocial' not in df_enriquecido.columns:
        if 'RazaoSocial_x' in df_enriquecido.columns:
            df_enriquecido = df_enriquecido.rename(columns={'RazaoSocial_x': 'RazaoSocial'})
        elif 'RazaoSocial_y' in df_enriquecido.columns:
            df_enriquecido = df_enriquecido.rename(columns={'RazaoSocial_y': 'RazaoSocial'})

    # montar DataFrame final com colunas solicitadas (usar 'cnpj_normalizado' como CNPJ)
    df_final = df_enriquecido.loc[:, [
        'cnpj_normalizado',
        'RazaoSocial',
        'Ano',
        'Trimestre',
        'ValorDespesas',
        'RegistroANS',
        'Modalidade',
        'UF',
        'conflito_cadastro'
    ]].copy()

    # renomear/formatar colunas de saída
    df_final = df_final.rename(columns={
        'cnpj_normalizado': 'CNPJ',
        'conflito_cadastro': 'ConflitoCadastro'
    })

    # logs de diagnóstico (resumo para auditoria)
    total_registros = len(df_final)
    
    registros_com_match = df_final['RegistroANS'].notna().sum()

    registros_sem_match = total_registros - int(registros_com_match)

    logger_enriquecimento.info(
        "Enriquecimento concluído: total=%d, matches=%d, unmatched=%d, cadastros_duplicados=%d, conflitos_detectados=%d",
        int(total_registros), int(registros_com_match), int(registros_sem_match), int(contador_duplicados), int(contador_conflitos)
    )

    logger_enriquecimento.info("Registros sem match permanecerão com NaN nas colunas RegistroANS/Modalidade/UF. Conflitos registrados separadamente para auditoria.")

    # salvar resultado em dados_enriquecidos/dados_enriquecidos.csv
    pasta_saida = os.path.join(os.path.dirname(diretorio_consolidado), "dados_enriquecidos")

    os.makedirs(pasta_saida, exist_ok=True)

    caminho_saida_principal = os.path.join(pasta_saida, "dados_enriquecidos.csv")
    
    df_final.to_csv(caminho_saida_principal, index=False, sep=';', encoding='utf-8-sig')

    logger_enriquecimento.info("Arquivo de enriquecimento salvo em: %s", caminho_saida_principal)

    # salvar arquivo de conflitos para auditoria (apenas se houver)
    # salvar arquivo de conflitos para auditoria (apenas se houver variações detectadas)
    if conflitos_lista:
        df_conflitos = pd.DataFrame(conflitos_lista)

        caminho_conflitos = os.path.join(pasta_saida, "cadastro_conflitos.csv")
        df_conflitos.to_csv(caminho_conflitos, index=False, sep=';', encoding='utf-8-sig')

        logger_enriquecimento.info("Arquivo de conflitos salvo em: %s (contém variações por CNPJ)", caminho_conflitos)
    else:
        logger_enriquecimento.info("Nenhum conflito de cadastro detectado.")

    return df_final


if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJETO_ROOT = os.path.dirname(SCRIPT_DIR)
    
    # Define a pasta raiz de dados (verifique se o nome é 'arquivos_csv_zips' ou 'arquivos_csv_zip')
    PASTA_DADOS_RAIZ = os.path.join(PROJETO_ROOT, 'arquivos_csv_zips')
    
    # Define as pastas de entrada com base na estrutura da raiz
    caminho_consolidado = os.path.join(PASTA_DADOS_RAIZ, "consolidado_despesas")
    caminho_cadastro = os.path.join(PASTA_DADOS_RAIZ, "dados_cadastrais")

    enriquecer_por_cadastro(caminho_consolidado, caminho_cadastro)