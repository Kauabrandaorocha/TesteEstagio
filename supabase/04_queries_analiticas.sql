-- QUERY 1

WITH despesas_por_trimestre AS (
    SELECT
        razao_social,
        ano,
        trimestre,
        SUM(valor_despesas) AS total_trimestre
    FROM consolidado_despesas
    WHERE valor_despesas IS NOT NULL
    GROUP BY razao_social, ano, trimestre
),

limites AS (
    SELECT
        razao_social,
        MIN(ano * 10 + trimestre) AS periodo_inicial,
        MAX(ano * 10 + trimestre) AS periodo_final
    FROM despesas_por_trimestre
    GROUP BY razao_social
),

valores_inicial_final AS (
    SELECT
        l.razao_social,
        di.total_trimestre AS valor_inicial,
        df.total_trimestre AS valor_final
    FROM limites l
    JOIN despesas_por_trimestre di
        ON di.razao_social = l.razao_social
       AND (di.ano * 10 + di.trimestre) = l.periodo_inicial
    JOIN despesas_por_trimestre df
        ON df.razao_social = l.razao_social
       AND (df.ano * 10 + df.trimestre) = l.periodo_final
    WHERE di.total_trimestre > 0
)

SELECT
    razao_social,
    valor_inicial,
    valor_final,
    ROUND(
        ((valor_final - valor_inicial) / valor_inicial) * 100,
        2
    ) AS crescimento_percentual
FROM valores_inicial_final
ORDER BY crescimento_percentual DESC
LIMIT 5;

-- QUERY 2

WITH despesas_por_uf AS (
    SELECT
        COALESCE(c.uf, 'NAO_INFORMADO') AS uf,
        d.cnpj,
        COALESCE(d.valor_despesas, 0) AS valor_despesas
    FROM consolidado_despesas d
    LEFT JOIN dados_cadastrais c
        ON d.cnpj = c.cnpj
)

SELECT
    uf,
    SUM(valor_despesas) AS total_despesas,
    CASE
        WHEN COUNT(DISTINCT cnpj) = 0 THEN 0
        ELSE SUM(valor_despesas) / COUNT(DISTINCT cnpj)
    END AS media_despesas_por_operadora
FROM despesas_por_uf
GROUP BY uf
ORDER BY total_despesas DESC
LIMIT 5;

-- QUERY 3

WITH media_por_trimestre AS (
    SELECT
        trimestre,
        AVG(valor_despesas) AS media_trimestre
    FROM consolidado_despesas
    GROUP BY trimestre
),

operadoras_acima_media AS (
    SELECT
        d.cnpj,
        d.trimestre,
        CASE
            WHEN d.valor_despesas > m.media_trimestre THEN 1
            ELSE 0
        END AS acima_media
    FROM consolidado_despesas d
    JOIN media_por_trimestre m
        ON d.trimestre = m.trimestre
),

contagem_por_operadora AS (
    SELECT
        cnpj,
        SUM(acima_media) AS trimestres_acima_media
    FROM operadoras_acima_media
    GROUP BY cnpj
)

SELECT
    COUNT(*) AS qtd_operadoras
FROM contagem_por_operadora
WHERE trimestres_acima_media >= 2;
