-- INDICES PARA OTIMIZAÇÃO DE CONSULTAS
CREATE INDEX idx_despesas_cnpj ON consolidado_despesas(cnpj);
CREATE INDEX idx_despesas_data ON consolidado_despesas(Ano, Trimestre);
CREATE INDEX idx_agregadas_razao_uf
ON despesas_agregadas(razao_social, uf);