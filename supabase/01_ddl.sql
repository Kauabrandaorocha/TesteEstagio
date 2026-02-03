-- TABELA DE DADOS CADASTRAIS DAS OPERADORAS ATIVAS 
CREATE TABLE IF NOT EXISTS dados_cadastrais (
    registro_operadora VARCHAR(50),
    cnpj VARCHAR(14) UNIQUE,
    razao_social VARCHAR(255),
    nome_fantasia VARCHAR(255),
    modalidade VARCHAR(100),
    logradouro VARCHAR(255),
    numero VARCHAR(20),
    complemento VARCHAR(100),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    uf CHAR(2),
    cep VARCHAR(10),
    ddd VARCHAR(5),
    telefone VARCHAR(20),
    fax VARCHAR(20),
    endereco_eletronico VARCHAR(255),
    representante VARCHAR(100),
    cargo_representante VARCHAR(100),
    regiao_de_comercializacao VARCHAR(100),
    data_registro_ans DATE
);

-- TABELA DE DADOS CONSOLIDADOS DE DESPESAS CNPJ
CREATE TABLE IF NOT EXISTS consolidado_despesas (
    id_despesa SERIAL PRIMARY KEY,
    cnpj VARCHAR(14),
    razao_social VARCHAR(255),
    ano INT NOT NULL,
    trimestre INT,
    valor_despesas DECIMAL(15, 2),

    CONSTRAINT fk_consolidado_despesas_cnpj FOREIGN KEY (cnpj) REFERENCES dados_cadastrais(cnpj) 
);

-- TABELA PARA DADOS AGREGADOS
CREATE TABLE IF NOT EXISTS despesas_agregadas (
    id_agregado SERIAL PRIMARY KEY,
    razao_social VARCHAR(255),
    uf CHAR(2),
    total_despesas DECIMAL(15, 2),
    media_trimestral DECIMAL(15, 2),
    desvio_padrao DECIMAL(15, 2)
);

-- CRIAÇÃO DE TABELAS DE STAGING PARA IMPORTAÇÃO DE DADOS, EVITANDO PROBLEMAS DE TIPOS E INCONSISTÊNCIAS

CREATE TABLE staging_consolidado_despesas (
    cnpj TEXT,
    razao_social TEXT,
    ano TEXT,
    trimestre TEXT,
    valor_despesas TEXT
);

CREATE TABLE staging_despesas_agregadas (
    razao_social TEXT,
    uf TEXT,
    total_despesas TEXT,
    media_trimestral TEXT,
    desvio_padrao TEXT
);

CREATE TABLE staging_dados_cadastrais (
    registro_operadora TEXT,
    cnpj TEXT,
    razao_social TEXT,
    nome_fantasia TEXT,
    modalidade TEXT,
    logradouro TEXT,
    numero TEXT,
    complemento TEXT,
    bairro TEXT,
    cidade TEXT,
    uf TEXT,
    cep TEXT,
    ddd TEXT,
    telefone TEXT,
    fax TEXT,
    endereco_eletronico TEXT,
    representante TEXT,
    cargo_representante TEXT,
    regiao_de_comercializacao TEXT,
    data_registro_ans TEXT
);