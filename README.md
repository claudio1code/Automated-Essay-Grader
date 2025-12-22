# ✍️ Automated-Essay-Grader - Corretor de Redações com IA

Bem-vindo ao **Projeto Mãe Redação**, uma solução inteligente para automatizar a correção de redações manuscritas. Utilizando o poder do modelo **Google Gemini 2.0 (Multimodal)**, o sistema lê imagens de textos manuscritos, realiza uma análise pedagógica completa baseada em competências e gera relatórios formatados em Word (.docx).

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Gemini API](https://img.shields.io/badge/AI-Google%20Gemini%202.0-orange)
![Architecture](https://img.shields.io/badge/Architecture-Service%20Layer-purple)

## 🚀 Funcionalidades

- **Leitura de Manuscritos**: Capacidade avançada de OCR e interpretação de texto manuscrito via IA.
- **Correção Pedagógica**: Avaliação detalhada baseada em competências (personalizável via prompt), com atribuição de notas e comentários construtivos.
- **Interface Web Amigável**: Aplicação interativa construída com Streamlit para uploads e correções individuais rápidas.
- **Processamento em Lote (Batch)**: Integração com o Google Drive para monitorar uma pasta, processar novas imagens automaticamente e salvar as correções em uma pasta de saída.
- **Arquitetura Modular**: Código organizado em serviços (`services/`), facilitando manutenção e expansão.
- **Configuração Segura**: Gerenciamento de credenciais via variáveis de ambiente e pasta `secrets/`.

## 📂 Estrutura do Projeto

O projeto segue o padrão **Service Layer**, separando a lógica de negócio dos scripts de execução:

<<<<<<< HEAD
* **Linguagem:** Python
* **Inteligência Artificial:** Google Gemini 1.5 Flash (Multimodal Vision + Text)
* **Interface:** Streamlit
* **Automação de Documentos:** Python-docx
* **Integração em Nuvem:** Google Drive API v3

## 🚀 Como Executar

### Pré-requisitos
* Python 3.10 ou superior
* Chave de API do Google Gemini (AI Studio)
* Credenciais do Google Cloud (para o módulo de Drive)

### Instalação

1. Clone o repositório:
   ```bash
   git clone [https://github.com/claudio1code/automated-essay-grader.git](https://github.com/claudio1code/automated-essay-grader.git)
   cd automated-essay-grader

2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   pip install -r requirements.txt

3. Configure as variáveis de ambiente: Crie um arquivo .env na raiz do projeto:
   ```bash
   GOOGLE_API_KEY="Sua_Chave_Gemini_Aqui"
Para o módulo de Drive, adicione o arquivo credentials.json e google-credentials.json (Service Account) na raiz.

**Rodando a Aplicação Web
Para utilizar a interface visual de correção individual:
   ```bash
   streamlit run app.py
  ```
Rodando a Automação em Lote (Google Drive)
Para monitorar e corrigir arquivos de uma pasta do Drive automaticamente:

   ```bash
   python corrigir_em_lote.py
````
📂 **Estrutura do Projeto**
=======
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
>>>>>>> 1e9df83 (update readme)
```

## 🛠️ Instalação e Configuração

### 1. Pré-requisitos
- Python 3.9+ instalado.
- Conta no **Google Cloud Platform (GCP)** com API Vertex AI/Gemini habilitada.
- (Opcional) Credenciais OAuth do **Google Drive API** para o modo lote.

### 2. Instalação
Clone o repositório e instale as dependências:

```bash
git clone https://github.com/seu-usuario/Corretor_redacao_AI.git
cd Corretor_redacao_AI

# Criar ambiente virtual
python -m venv venv
# Ativar (Windows)
venv\Scripts\activate
# Ativar (Linux/Mac)
source venv/bin/activate

# Instalar pacotes
pip install -r requirements.txt
```
🧠 **Desafios Técnicos Superados**
Engenharia de Prompt com JSON: Configuração do modelo para retornar estritamente um JSON válido, evitando erros de parseamento na geração do documento final.

### 3. Configuração de Credenciais
Este projeto utiliza uma pasta `secrets/` para organizar chaves de API.

1.  Crie a pasta `secrets/` na raiz do projeto.
2.  Coloque o arquivo da sua Service Account do Google Cloud lá dentro (ex: `google-credentials.json`).
3.  (Para Drive) Coloque o `credentials.json` do OAuth Client lá dentro.

📄 **Licença**
Este projeto está sob a licença MIT - veja o arquivo LICENSE para detalhes.
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
Este projeto é distribuído sob a licença MIT.
