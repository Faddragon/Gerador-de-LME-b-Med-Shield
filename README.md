# b-Med Shield | Gerador de LME AI

<img width="2816" height="1536" alt="logo" src="https://github.com/user-attachments/assets/d74f451a-b909-4c60-9dad-3288e1a662e1" />


Sistema arquitetado sob o paradigma "Local-First", em estrita conformidade com a Lei Geral de Proteção de Dados (LGPD), destinado à automação do preenchimento de Laudos de Solicitação, Avaliação e Autorização de Medicamentos do Componente Especializado da Assistência Farmacêutica (LME) do Sistema Único de Saúde (SUS), com foco operacional nas diretrizes da Secretaria de Estado da Saúde de São Paulo.

## 1. Escopo e Problematização
O fluxo de prescrição de medicamentos de alto custo requer o preenchimento de formulários estruturados e a observância rigorosa aos Protocolos Clínicos e Diretrizes Terapêuticas (PCDT). Inconsistências de dados, omissão de exames obrigatórios ou relatórios clínicos incompletos resultam em glosas administrativas, atrasos na dispensação e ineficiência operacional no ambiente ambulatorial.

## 2. Proposta de Valor e Arquitetura da Solução
O b-Med Shield opera primariamente como um Sistema de Suporte à Decisão Clínica (CDSS), provendo uma interface de preenchimento automatizado que impõe conformidade técnica *in-app*, mitigando erros estruturais de preenchimento antes da submissão do processo farmacêutico.

### 2.1. Funcionalidades Core
* **Extração de Dados via Regex (Smart Paste):** Parser client-side que processa o *string* bruto do prontuário eletrônico, extraindo e sanitizando dados referentes a Nome, Filiação, CPF e CNS via expressões regulares e mapeamento de padrões sintáticos.
* **Resolução Dinâmica de Entidades (CNES):** Implementação de busca bidirecional *offline* (Nome <-> CNES) baseada em estrutura de dados de dicionário (hash map) gerada a partir das bases oficiais do DataSUS, otimizando o *time-to-task* do prescritor.
* **Validação de Conformidade PCDT (Gatekeeper):** Motor de regras de negócio que intercepta a requisição de impressão, validando os requisitos mínimos (exames sorológicos/imagem e refratariedade prévia) específicos do CID e do princípio ativo selecionados, exigindo *opt-in* explícito de auditoria do prescritor.
* **Renderização Nativa de Protocolos:** Integração de visualizador no *Document Object Model* (DOM) via IFrame para exibição do PCDT governamental (.pdf) local, reduzindo a carga cognitiva de busca bibliográfica externa.
* **Motor de Impressão via DOM (Glass Mask Pattern):** Subversão do uso de bibliotecas de manipulação de PDF (como pypdf/AcroForms) em favor da injeção direta de variáveis via DOM sobre uma camada base rasterizada do formulário oficial, garantindo precisão de coordenadas de impressão via CSS (`@page` e posicionamento absoluto).

## 3. Stack Tecnológica e Dependências
* **Backend:** Python 3.9+, framework Flask (Roteamento restrito de recursos estáticos e templates HTML).
* **Frontend:** HTML5, Vanilla JavaScript (ES6+), CSS3, UI Framework Bootstrap 5.
* **ETL e Persistência de Referência:** Arquivos flat (.xlsx) processados via bibliotecas `pandas` e `openpyxl`, serializados dinamicamente em formato JSON e envelopados como scripts estáticos (.js) para consumo client-side.
* **Arquitetura de Dados:** Aplicação baseada em estado local de sessão, dispensando requisições a bancos de dados relacionais externos (RDBMS) ou APIs RESTful de terceiros na camada de operação ambulatorial.

## 4. Estrutura de Diretórios

```text
bmed-lme-app/
├── server.py                 # Roteador WSGI principal (Flask)
├── atualizar_banco.py        # Script ETL (XLSX -> JS File)
├── requirements.txt          # Mapeamento de dependências Python
├── .env.example              # Template de variáveis de ambiente
├── data/                     # Diretório de persistência de assets restritos
│   ├── banco_dados_lme_com_anamnese.xlsx  # Tabela verdade de correlação medicamentosa e anamnese
│   └── pcdt 12-4-26/         # Repositório de assets em formato PDF (Protocolos SUS)
├── public/                   # Diretório de distribuição de assets estáticos
│   ├── index.html            # Entry point da UI
│   ├── app_logic.js          # Lógica de controle e DOM manipulation
│   ├── banco_dados.js        # Objeto JSON de referência (Gerado pelo atualizar_banco.py)
│   └── lme_fundo.png         # Asset gráfico para impressão rasterizada
└── templates/                
    └── lme_impressao.html    # Template de renderização de impressão via Jinja2
