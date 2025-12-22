# ✍️ AI Essay Grader - Corretor de Redações com IA

Bem-vindo ao **AI Essay Grader**, uma solução inteligente para automatizar a correção de redações manuscritas. Utilizando o poder do modelo **Google Gemini 2.0 (Multimodal)**, o sistema lê imagens de textos manuscritos, realiza uma análise pedagógica completa baseada em competências e gera relatórios formatados em Word (.docx).

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Gemini API](https://img.shields.io/badge/AI-Google%20Gemini%202.0-orange)
![Architecture](https://img.shields.io/badge/Architecture-Service%20Layer-purple)
![License](https://img.shields.io/badge/License-Apache%202.0-green)

## 🚀 Funcionalidades

- **Leitura de Manuscritos**: Capacidade avançada de OCR e interpretação de texto manuscrito via IA.
- **Correção Pedagógica**: Avaliação detalhada baseada em competências (personalizável via prompt), com atribuição de notas e comentários construtivos.
- **Interface Web Amigável**: Aplicação interativa construída com Streamlit para uploads e correções individuais rápidas.
- **Processamento em Lote (Batch)**: Integração com o Google Drive para monitorar uma pasta, processar novas imagens automaticamente e salvar as correções em uma pasta de saída.
- **Arquitetura Modular**: Código organizado em serviços (`services/`), facilitando manutenção e expansão.
- **Configuração Segura**: Gerenciamento de credenciais via variáveis de ambiente e pasta `secrets/`.

## 📂 Estrutura do Projeto

O projeto segue o padrão **Service Layer**, separando a lógica de negócio dos scripts de execução:

```text
Corretor_redacao_AI/
├── app.py                  # Interface Web (Frontend Streamlit)
├── corrigir_em_lote.py     # Script de automação via Google Drive
├── health_check.py         # Script de diagnóstico do sistema
├── config.py               # Gerenciador de configurações centralizado
├── services/               # Camada de Serviços (Lógica de Negócio)
│   ├── ai_service.py       # Comunicação com Google Gemini
│   ├── drive_service.py    # Comunicação com Google Drive
│   └── report_service.py   # Geração de arquivos .docx
├── assets/                 # Recursos Estáticos
│   ├── prompt.txt          # Prompt System com critérios de correção
│   └── template.docx       # Modelo base para o relatório final
├── secrets/                # Pasta segura para credenciais (ignorada pelo Git)
└── .env                    # Variáveis de ambiente
```

## 🛠️ Instalação e Configuração

### 1. Pré-requisitos
- Python 3.10+ instalado.
- Conta no **Google Cloud Platform (GCP)** com API Vertex AI/Gemini habilitada.
- (Opcional) Credenciais OAuth do **Google Drive API** para o modo lote.

### 2. Instalação
Clone o repositório e instale as dependências:

```bash
git clone https://github.com/claudio1code/ProjetoMaeRedacao.git
cd ProjetoMaeRedacao

# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate
# Ativar (Linux/Mac)
source venv/bin/activate

# Instalar pacotes
pip install -r requirements.txt
```

### 3. Configuração de Credenciais
Este projeto utiliza uma pasta `secrets/` para organizar chaves de API com segurança.

1.  Crie a pasta `secrets/` na raiz do projeto.
2.  Coloque o arquivo da sua Service Account do Google Cloud lá dentro (ex: `google-credentials.json`).
3.  (Para Drive) Coloque o `credentials.json` do OAuth Client lá dentro.

Configure o arquivo `.env`:
```bash
cp .env.example .env
```
Edite o `.env` e ajuste os nomes dos arquivos e IDs das pastas do Drive:
```ini
GOOGLE_CREDENTIALS_FILE=google-credentials.json
DRIVE_FOLDER_INPUT_ID=seu_id_da_pasta_entrada
DRIVE_FOLDER_OUTPUT_ID=seu_id_da_pasta_saida
GEMINI_MODEL_NAME=gemini-2.0-flash
```

## 💻 Como Usar

### 🏥 Diagnóstico (Health Check)
Antes de começar, verifique se tudo está conectado corretamente:
```bash
python health_check.py
```
*Se houver erros, o script indicará exatamente o que está faltando.*

### 🌐 Interface Web (Correção Individual)
Ideal para correções rápidas e visuais.
```bash
streamlit run app.py
```

### 🤖 Automação em Lote (Google Drive)
Monitora a pasta do Drive definida no `.env`, corrige as imagens que encontrar e salva os Docs na pasta de saída.
```bash
python corrigir_em_lote.py
```

## 🧩 Personalização

- **Critérios de Correção**: Edite `assets/prompt.txt`.
- **Layout do Relatório**: Edite `assets/template.docx`.

## 📄 Licença

Este projeto é distribuído sob a licença **Apache 2.0**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.