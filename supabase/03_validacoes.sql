
-- INSERÇÃO NA TABELA DE CONSOLIDADO DE DESPESAS
INSERT INTO consolidado_despesas (
    cnpj,
    razao_social,
    ano,
    trimestre,
    valor_despesas
)
SELECT
    -- CNPJ: remove caracteres não numéricos
    REGEXP_REPLACE(cnpj, '[^0-9]', '', 'g') AS cnpj,

    NULLIF(TRIM(razao_social), '') AS razao_social,

    -- Ano: só entra se for número válido (ex: 2022)
    ano::INT,

    -- Trimestre: aceita apenas 1 a 4
    trimestre::INT,

    -- Valor: troca vírgula por ponto, converte para decimal
    NULLIF(
        REPLACE(
            REGEXP_REPLACE(valor_despesas, '[^0-9,]', '', 'g'),
            ',', '.'
        ),
        ''
    )::DECIMAL(15,2) AS valor_despesas

FROM staging_consolidado_despesas

WHERE
    -- evita anos inválidos
    ano ~ '^\d{4}$'

    -- trimestre válido
    AND trimestre IN ('1','2','3','4');

-- INSERÇÃO NA TABELA DE DADOS CADASTRAIS
INSERT INTO dados_cadastrais (
    registro_operadora,
    cnpj,
    razao_social,
    nome_fantasia,
    modalidade,
    logradouro,
    numero,
    complemento,
    bairro,
    cidade,
    uf,
    cep,
    ddd,
    telefone,
    fax,
    endereco_eletronico,
    representante,
    cargo_representante,
    regiao_de_comercializacao,
    data_registro_ans
)
SELECT
    NULLIF(TRIM(registro_operadora), '') AS registro_operadora,
    -- CNPJ: remove caracteres não numéricos
    REGEXP_REPLACE(cnpj, '[^0-9]', '', 'g') AS cnpj,

    NULLIF(TRIM(razao_social), '') AS razao_social,
    NULLIF(TRIM(nome_fantasia), '') AS nome_fantasia,
    NULLIF(TRIM(modalidade), '') AS modalidade,     
    NULLIF(TRIM(logradouro), '') AS logradouro,
    NULLIF(TRIM(numero), '') AS numero,
    NULLIF(TRIM(complemento), '') AS complemento,
    NULLIF(TRIM(bairro), '') AS bairro,
    NULLIF(TRIM(cidade), '') AS cidade,
    NULLIF(TRIM(uf), '') AS uf,
    NULLIF(TRIM(cep), '') AS cep,
    NULLIF(TRIM(ddd), '') AS ddd,
    NULLIF(TRIM(telefone), '') AS telefone,
    NULLIF(TRIM(fax), '') AS fax,
    NULLIF(TRIM(endereco_eletronico), '') AS endereco_eletronico,
    NULLIF(TRIM(representante), '') AS representante,
    NULLIF(TRIM(cargo_representante), '') AS cargo_representante,
    NULLIF(TRIM(regiao_de_comercializacao), '') AS regiao_de_comercializacao,
    

    CASE
        WHEN data_registro_ans ~ '^\d{4}-\d{2}-\d{2}$'
            THEN data_registro_ans::DATE
        WHEN data_registro_ans ~ '^\d{2}/\d{2}/\d{4}$'
            THEN TO_DATE(data_registro_ans, 'DD/MM/YYYY')
        ELSE NULL
    END AS data_registro_ans

FROM staging_dados_cadastrais

WHERE
    -- evita cnpjs inválidos
    REGEXP_REPLACE(cnpj, '[^0-9]', '', 'g') ~ '^\d{14}$'

    -- evita ufs inválidos
    AND uf ~ '^[A-Z]{2}$';

-- INSERÇÃO NA TABELA DE DESPESAS AGREGADAS

INSERT INTO despesas_agregadas (
    razao_social,
    uf,
    total_despesas,
    media_trimestral,
    desvio_padrao
)
SELECT  
    NULLIF(TRIM(razao_social), '') AS razao_social, 

    NULLIF(TRIM(uf), '') AS uf,

    -- Total Despesas
    NULLIF(
        REPLACE(total_despesas, ',', '.'),
        ''
    )::DECIMAL(15,2) AS total_despesas,

    -- Média Trimestral
    NULLIF(
        REPLACE(media_trimestral, ',', '.'),
        ''
    )::DECIMAL(15,2) AS media_trimestral,

    -- Desvio Padrão
    NULLIF(
        REPLACE(desvio_padrao, ',', '.'),
        ''
    )::DECIMAL(15,2) AS desvio_padrao

FROM staging_despesas_agregadas;
