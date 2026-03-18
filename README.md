# 📊 Sistema de Ingestão e Análise de Dados de Saúde (ANS)
Parte 1 – Coleta, Processamento e Consolidação de Dados
## 📌 Objetivo

Esta etapa tem como objetivo consumir dados públicos da ANS (Agência Nacional de Saúde Suplementar), processar arquivos contábeis referentes aos últimos 3 trimestres disponíveis e consolidar as informações de despesas em um único arquivo estruturado.

## 🌐 Fonte dos Dados

Os dados são obtidos da API pública da ANS:
```bash
https://dadosabertos.ans.gov.br/FTP/PDA/
```

Os arquivos são organizados por:
```bash
ANO/TRIMESTRE
Exemplo:
2024/1T/
2024/2T/
2024/3T/
```

## 🏗️ Arquitetura da Solução

O processo foi dividido em dois scripts principais para melhorar organização, manutenção e reutilização do código:

### 1️⃣ extraír_zips.py

Responsável por:

- Acessar o diretório público da ANS

- Identificar os 3 trimestres mais recentes disponíveis

- Baixar automaticamente os arquivos ZIP

- Extrair o conteúdo dos arquivos baixados

## 2️⃣ processar_arquivos.py

Responsável por:

- Identificar arquivos contendo despesas com eventos/sinistros

- Processar arquivos em múltiplos formatos:

  - CSV

  - TXT

  - XLSX

- Normalizar estruturas diferentes de colunas

- Tratar inconsistências nos dados

- Consolidar os dados em um único CSV

- Compactar o resultado final em um arquivo ZIP

## ▶️ Como Executar
### ✅ Pré-requisitos

- Python 3.10+

- Ambiente virtual recomendado
```bash
python -m venv venv
```
- Ativação MacOS/Linux
```bash
source venv\bin\activate
```
- Ativação Windows
```bash
venv\scripts\activate
```

## 📦 Instalação de dependências

```bash
pip install -r requirements.txt
```

## 📥 Passo 1 – Preparação do Ambiente e Extração
Execute o comando inicial:

```bash
python scripts/extrair_zips.py
```
O que este script faz:

- **Autoconfiguração de Pastas**: Cria automaticamente toda a estrutura de diretórios necessária para o fluxo de dados (arquivos_extraidos, consolidado_despesas, dados_enriquecidos, etc.), garantindo que o projeto funcione mesmo se as pastas de destino não existirem.

- **Extração de Dados**: Localiza os arquivos ZIP dos últimos 3 trimestres na pasta arquivoszip e extrai os CSVs brutos para a pasta de processamento.

- **Nota**: Certifique-se de que seus arquivos `.zip` originais e o arquivo `Relatorio_cadop.csv` estejam em suas respectivas pastas dentro de `arquivos_csv_zips/` antes de iniciar.

## 📊 Passo 2 – Processar e Consolidar Dados

Execute:
```bash
python processar_arquivos.py
```

Este script irá:

- Ler os arquivos extraídos

- Identificar dados de despesas

- Normalizar estrutura dos arquivos

- Consolidar os dados

Gerar:
```python
consolidado_despesas.csv
consolidado_despesas.zip
```

# ⚙️ Decisões Técnicas e Trade-offs
## 🧠 Processamento de Arquivos
### Escolha: Processamento Incremental (Streaming)
### Alternativa Considerada:

- Carregar todos os arquivos em memória simultaneamente

### Decisão:

Foi adotado o processamento incremental, lendo os arquivos individualmente e consolidando os dados gradualmente.

### Justificativa:

- ✔ Melhor escalabilidade
- ✔ Menor consumo de memória
- ✔ Permite lidar com arquivos grandes
- ✔ Reduz risco de falhas por limitação de RAM

### Trade-off:

- ❌ Pode aumentar levemente o tempo total de processamento
- ❌ Implementação um pouco mais complexa

## 🧠 Suporte a Múltiplos Formatos

Os arquivos da ANS podem variar entre:

- CSV

- TXT

- XLSX

### Estratégia adotada:

Foi implementada detecção automática de formato com normalização das colunas necessárias.

Justificativa:

- ✔ Torna o sistema resiliente a mudanças no padrão dos dados
- ✔ Reduz manutenção futura

## 🧠 Normalização de Estrutura

Os arquivos apresentam diferenças como:

- Nomes de colunas distintos

- Estruturas inconsistentes

- Formatos de data variados

Estratégia adotada:

- Mapeamento de colunas equivalentes

- Padronização para o seguinte formato:
```bash
CNPJ
RazaoSocial
Trimestre
Ano
ValorDespesas
```
## ⚠️ Tratamento de Inconsistências

Durante a consolidação, foram identificados três principais tipos de inconsistência:

## 🔹 CNPJs duplicados com razões sociais diferentes
### Estratégia:

Manter os registros e considerar a razão social mais recente encontrada.

### Justificativa:

Diferenças podem ocorrer devido a mudanças cadastrais ou divergências de base. Remover dados poderia gerar perda de informação relevante.

## 🔹 Valores zerados ou negativos
### Estratégia:

Manter registros e permitir análise posterior.

### Justificativa:

- Valores negativos podem representar ajustes contábeis válidos.
- Remoção automática poderia comprometer a integridade financeira.

## 🔹 Formatos inconsistentes de trimestre
### Estratégia:

Conversão para formato padronizado numérico:
```bash
Ano: YYYY
Trimestre: 1, 2, 3 ou 4
```
### Justificativa:

Facilita análise e integração com banco de dados.

## 📦 Compactação do Resultado

O arquivo consolidado é compactado em:
```bash
consolidado_despesas.zip
```
Justificativa:

- ✔ Reduz tamanho para armazenamento e envio
- ✔ Facilita distribuição do dataset

## 📂 Estrutura de Saída
```bash
dados_extraidos/
consolidado_despesas.csv
consolidado_despesas.zip
```
## 🚀 Possíveis Melhorias Futuras

- Paralelização do processamento

- Validação estatística automática de inconsistências

- Persistência direta em banco de dados

- Monitoramento de novas versões dos arquivos da ANS


# 📊 Teste Técnico – Transformação e Validação de Dados
## Parte 2 – Validação, Enriquecimento e Agregação
## 📌 Objetivo

Esta etapa tem como objetivo validar, enriquecer e agregar os dados consolidados na Parte 1, garantindo integridade, consistência e geração de métricas analíticas relevantes sobre despesas das operadoras.

## ▶️ Fonte de Dados Utilizada
### 📁 Arquivo Base

Gerado na Parte 1:
```bash
consolidado_despesas.csv
```
### 📁 Dados Cadastrais das Operadoras

Obtido em:
```bash
https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/
```
## 🏗️ Arquitetura da Solução

O processamento foi dividido em três etapas principais:

1 - Validação de dados

2 - Enriquecimento com dados cadastrais

3 - Agregação e análise estatística

## ✅ 2.1 Validação de Dados
## 🔍 Validações Implementadas
### ✔ Validação de CNPJ

- Foram verificadas duas condições:

- Formato válido (14 dígitos numéricos)

- Dígitos verificadores corretos

### ✔ Validação de Valores Financeiros

Critérios aplicados:

- Conversão para tipo numérico

- Identificação de valores inválidos

### ✔ Validação de Razão Social

Critérios:

- Campo não pode ser nulo

- Campo não pode ser vazio

## ⚙️ Trade-off – Tratamento de CNPJs Inválidos
Alternativas Consideradas
| Estratégia | Vantagens | Desvantagens |
|------------|-----------|--------------|
| Remover registros inválidos | Garante integridade dos dados | Possível perda de dados relevantes |
| Corrigir automaticamente | Mantém volume de dados | Alto risco de gerar dados incorretos |
| Marcar como inválido | Mantém rastreabilidade | Aumenta complexidade analítica |

## ✅ Estratégia Escolhida: Remoção de Registros com CNPJ Inválido
### Justificativa:

- CNPJ é chave primária de relacionamento

- Registros inválidos comprometeriam joins futuros

- Garante maior confiabilidade analítica

### Trade-off Aceito:

- ❌ Perda potencial de dados
- ✔ Maior consistência estrutural

## 🔗 2.2 Enriquecimento com Dados Cadastrais
### 📥 Etapas Realizadas

1 - Download do CSV de operadoras ativas

2 - Normalização do campo CNPJ

3 - Join entre dados consolidados e cadastro

### 📌 Colunas Adicionadas
```bash
RegistroANS
Modalidade
UF
```
## ⚠️ Análise de Inconsistências Encontradas
### 🔹 Registros Sem Correspondência no Cadastro
Estratégia:

Manter os registros e preencher campos com:
```bash
NAO_INFORMADO
```
Justificativa:

- Pode existir defasagem entre bases

- Mantém histórico financeiro completo

### 🔹 CNPJs Duplicados no Cadastro
Estratégia:

Selecionar o registro mais recente com base na data de registro ANS.

Justificativa:

- Dados mais atualizados tendem a refletir a situação atual da operadora

- Evita duplicidade no join

## ⚙️ Trade-off – Estratégia de Join
Alternativas Consideradas
| Estratégia | Vantagens | Desvantagens |
|------------|-----------|--------------|
| Join em memória com Pandas | Alta performance e simplicidade | Alto consumo de memória |
| Join incremental via streaming | Baixo uso de memória | Código mais complexo |
| Join em banco de dados | Alta escalabilidade | Maior overhead de infraestrutura |

### ✅ Estratégia Escolhida: Join em Memória com Pandas
Justificativa:

- Volume de dados compatível com memória disponível

- Simplicidade de implementação

- Melhor performance para análise exploratória

### Trade-off Aceito:

- ❌ Escalabilidade limitada para volumes extremamente grandes
- ✔ Maior produtividade e clareza de código

## 📊 2.3 Agregação e Análise Estatística
### 📌 Agrupamento Implementado

Os dados foram agrupados por:
```bash
RazaoSocial
UF
```
### 📈 Métricas Calculadas
✔ Total de Despesas
```bash
SUM(valor_despesas)
```

Representa o volume financeiro total por operadora e estado.

✔ Média de Despesas por Trimestre
```bash
MEAN(valor_despesas)
```

Permite avaliar padrão de gastos.

✔ Desvio Padrão das Despesas
```bash
STD(valor_despesas)
```

Utilizado para identificar variabilidade financeira entre períodos.

## ⚙️ Trade-off – Estratégia de Ordenação
Alternativas Consideradas
| Estratégia | Vantagens | Desvantagens |
|------------|-----------|--------------|
| Ordenação em memória | Alta performance para volumes moderados | Pode escalar mal com Big Data |
| Ordenação incremental | Melhor uso de memória | Complexidade maior |
| Ordenação via banco | Alta escalabilidade | Necessita infraestrutura adicional |

### ✅ Estratégia Escolhida: Ordenação em Memória

Os dados foram ordenados por:

- Total de despesas (decrescente)

Justificativa:

- Volume de dados permite processamento em memória

- Maior simplicidade e velocidade de execução

### Trade-off Aceito:

- ❌ Menor escalabilidade para datasets massivos
- ✔ Melhor performance local

## 📦 Arquivos Gerados
###📁 Resultado Final
```bash
despesas_agregadas.csv
```

Contendo:
```bash
RazaoSocial
UF
TotalDespesas
MediaDespesas
DesvioPadraoDespesas
```
## 📦 Compactação Final

O resultado é compactado em:
```bash
Teste_Salomao.zip
```

🚀 Execução
```bash
python transformar_dados.py
```

O script irá:

- Validar dados

- Realizar enriquecimento cadastral

- Executar agregações estatísticas

- Gerar arquivos finais

- Compactar resultado

## 🧠 Decisões Técnicas Gerais
✔ Uso de Pandas para Transformações
Motivos:

- Alta produtividade

- Manipulação eficiente de dados tabulares

- Biblioteca padrão para análise de dados em Python

✔ Estrutura Modular

- Separação de responsabilidades entre:

- Validação

- Enriquecimento

- Agregação

- Facilitando manutenção e testes.

# 📘 Parte 3: Banco de Dados e Análise
## 🗄️ Ambiente de Banco de Dados

Para implementação do banco de dados foi utilizado PostgreSQL hospedado em nuvem através do Supabase.

O Supabase foi escolhido por fornecer:

- PostgreSQL gerenciado

- Facilidade de deploy e acesso remoto

- Interface visual para inspeção de tabelas e dados

- Boa integração com APIs backend

- Possibilidade de simular ambiente real de produção

### 🔐 Sobre acesso ao banco

Por questões de segurança, as credenciais do banco não foram disponibilizadas publicamente.

No entanto:

- O schema completo pode ser recriado executando os scripts SQL incluídos neste repositório

- Os dados podem ser importados utilizando os CSVs gerados nos testes anteriores

👉 Isso garante reprodutibilidade total do ambiente.

### 📦 Estrutura do Banco

Os scripts SQL criam três grupos principais de tabelas:

### 1️⃣ Dados cadastrais das operadoras

Armazena informações institucionais das operadoras.

### 2️⃣ Dados consolidados de despesas

Armazena despesas trimestrais por operadora.

### 3️⃣ Dados agregados

Armazena estatísticas consolidadas para análises analíticas.

## ⚖️ Trade-off Técnico — Normalização
✔ Opção escolhida: Modelo Normalizado

Os dados foram separados em múltiplas tabelas relacionadas.

Motivações
| Critério | Justificativa |
|----------|--------------|
| Volume de dados | Evita redundância e reduz armazenamento |
| Frequência de atualização | Dados cadastrais mudam menos que despesas |
| Queries analíticas | Facilita agregações e joins eficientes |

Alternativa considerada

Modelo desnormalizado foi descartado pois:

- Aumentaria duplicação de dados

- Maior custo de atualização

- Maior risco de inconsistências

## ⚖️ Trade-off Técnico — Tipos de Dados
### 💰 Valores Monetários 
✔ Opção escolhida: DECIMAL(15,2)

Motivo:

- Mantém precisão financeira

- Evita erros de arredondamento do FLOAT

- Compatível com cálculos analíticos

### 📅 Datas
✔ Opção escolhida: DATE

Motivo:

- Permite operações nativas de comparação e filtragem

- Evita parsing manual de strings

- Melhor performance para queries temporais

### 📥 Estratégia de Importação dos CSVs

A importação foi realizada utilizando tabelas staging intermediárias.

✔ Motivos

- Permite validação antes de inserir em tabelas finais

- Facilita tratamento de inconsistências

- Evita falhas totais durante importação

### 🔎 Tratamento de Inconsistências
NULL em campos obrigatórios

Estratégia adotada:

- Conversão para NULL

- Filtragem via validações SQL

Motivo:

- Evita perda de registros válidos parcialmente

### Strings em campos numéricos

Estratégia adotada:

- Limpeza via regex

- Conversão segura para DECIMAL

### Datas inconsistentes

Estratégia adotada:

- Conversão automática para formatos aceitos

- Datas inválidas convertidas para NULL

## 📊 Queries Analíticas
### 🔹 Query 1 — Crescimento percentual de despesas

Objetivo:
Identificar as 5 operadoras com maior crescimento entre o primeiro e último trimestre.

Desafio tratado

Operadoras sem dados em todos os trimestres.

Estratégia adotada

Comparar apenas operadoras que possuem dados em ambos períodos.

Motivo:
Garante cálculo percentual confiável.

### 🔹 Query 2 — Distribuição de despesas por UF

Objetivos:

- Total de despesas por estado

- Média por operadora

Estratégia:
Utilização de agregações SQL com JOIN entre despesas e dados cadastrais.

### 🔹 Query 3 — Operadoras acima da média geral

Objetivo:
Identificar operadoras com despesas acima da média em pelo menos dois trimestres.

Estratégia adotada

Uso de subqueries e agregações condicionais.

Motivo:
Melhor legibilidade e manutenção do código.

## ☁️ Sobre Hospedagem em Nuvem (Supabase)

O banco foi implantado em ambiente cloud para simular cenário real de produção.

## Imagens

- Tabelas
<img width="1903" height="869" alt="image" src="https://github.com/user-attachments/assets/cc7bcb78-dd8e-4c3f-a531-9e819f23d1b8" />

- Schemas
<img width="1590" height="791" alt="image" src="https://github.com/user-attachments/assets/c01b6b99-cede-45a1-866c-3d3207ce61a0" />


# 🚀 Etapa 4: Servidor de Dados e Interface Web (ANS Insight)
Este módulo consiste em uma aplicação Full Stack para visualização e análise de dados das operadoras de saúde suplementar, integrando um backend em Python com um frontend em Vue.js 3.

## 🛠️ Tecnologias Utilizadas
- Backend: Python 3.9+, Flask, Psycopg2 (Conexão PostgreSQL), Gunicorn.

- Frontend: Vue.js 3 (Composition API), Vite, Axios, Chart.js.

- Banco de Dados: PostgreSQL (Hospedado no Supabase).

- API Testing: Postman (Coleção inclusa no repositório).

## 🧠 Trade-offs Técnicos e Justificativas
### 🰠 Backend (Flask)
- Framework (Flask): Escolhido pela simplicidade e arquitetura plugável. Para um projeto focado em endpoints de consulta e processamento de dados, o Flask oferece a agilidade necessária com menor sobrecarga (overhead) que frameworks mais robustos.

- Estratégia de Paginação (Offset-based): Implementada via LIMIT e OFFSET no SQL. Justifica-se pelo volume de dados moderado e pela necessidade do usuário de navegar para páginas específicas rapidamente, sendo a abordagem mais intuitiva para interfaces de tabelas.

- Cálculo de Estatísticas (Query Direta): Optou-se por calcular os dados em tempo real. Dado que a base da ANS é atualizada trimestralmente, a consistência é prioritária e a performance do PostgreSQL com índices é suficiente para o volume atual sem necessidade de cache complexo.

- Estrutura de Resposta (Dados + Metadados): A API retorna um objeto contendo o array de dados e um objeto meta (total, página atual). Isso facilita o controle do componente de paginação no Vue.js sem necessidade de chamadas extras para contar registros.

## 🎨 Frontend (Vue.js)
- Busca/Filtro (Servidor): A busca é realizada via API (Backend). Isso garante que, mesmo que a base cresça para milhares de registros, a aplicação permaneça leve, evitando o download desnecessário de toda a base para o navegador do cliente.

- Gerenciamento de Estado (Composables/Reactive): Utilizou-se o padrão nativo do Vue 3 para gerenciar o estado global de busca e filtros. É mais leve que o Pinia e oferece excelente reatividade para este escopo.

- Tratamento de Erros e Loading:

   - Loading: Skeleton screens ou spinners indicam processamento.

   - Erros: Mensagens específicas (ex: "Operadora não encontrada") em vez de erros genéricos, melhorando a UX.

   - Dados Vazios: Implementado estado visual informativo para operadoras sem registros financeiros (conforme validado nos testes).

## 🏃 Como Executar o Projeto
### 1. Backend (Python/Flask)
Certifique-se de ter o Python instalado.

```bash
cd backend
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate # Linux/Mac ou venv\Scripts\activate no Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar Variável de Ambiente (Supabase)
# No Windows: set DATABASE_URL=sua_url_do_supabase / URL do banco local
# No Linux: export DATABASE_URL=sua_url_do_supabase / URL do banco local

# Rodar o servidor
python app.py
```
2. Frontend (Vue.js)

```bash
cd frontend
# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev
```
Acesse http://localhost:5173 no navegador.

### 3. Testando a API (Postman)
- Importe o arquivo Api_operadoras_collection.json no seu Postman.

- Certifique-se de que a variável baseUrl está apontando para http://localhost:5000.

- Utilize os exemplos salvos para visualizar as respostas esperadas.

## 📈 Funcionalidades Implementadas
- Listagem paginada de operadoras.

- Busca por Razão Social ou CNPJ.

- Dashboard com Dashboard com gráficos de despesas por UF e TOP 5.

- Detalhamento individual com gráfico de evolução histórica de despesas.

- Tratamento de zeros à esquerda em CNPJs para integridade de dados.

## Observações Finais
- Este projeto foi desenvolvido como parte de um desafio técnico, focando em boas práticas de engenharia de dados, performance e escalabilidade.
