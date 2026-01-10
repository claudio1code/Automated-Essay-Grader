import os

from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env, se existir
load_dotenv()


class Config:
    # Caminhos Base
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
    SECRETS_DIR = os.path.join(BASE_DIR, "secrets")

    # Arquivos de Credenciais
    GOOGLE_CREDENTIALS_PATH = os.path.join(
        SECRETS_DIR, os.getenv("GOOGLE_CREDENTIALS_FILE", "google-credentials.json")
    )
    DRIVE_CREDENTIALS_PATH = os.path.join(
        SECRETS_DIR, os.getenv("DRIVE_CREDENTIALS_FILE", "credentials.json")
    )
    DRIVE_TOKEN_PATH = os.path.join(
        SECRETS_DIR, os.getenv("DRIVE_TOKEN_FILE", "token.json")
    )

    # Arquivos de Recursos
    TEMPLATE_DOCX_PATH = os.path.join(
        ASSETS_DIR, os.getenv("TEMPLATE_DOCX_FILE", "template.docx")
    )
    PROMPT_PATH = os.path.join(ASSETS_DIR, os.getenv("PROMPT_FILE", "prompt.txt"))

    # Diretório Temporário
    TMP_DIR = os.path.join(BASE_DIR, os.getenv("TMP_DIR", "tmp"))

    # Configurações da IA
    MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-pro")

    # Configurações do Google Drive (Correção em Lote)
    DRIVE_FOLDER_INPUT_ID = os.getenv(
        "DRIVE_FOLDER_INPUT_ID", "1c_8ybbo6HAhMxlOeNKX71PPF8TfySKx-"
    )
    DRIVE_FOLDER_OUTPUT_ID = os.getenv(
        "DRIVE_FOLDER_OUTPUT_ID", "16xRIPkBY8gRp9vNzxgH1Ex4GhTnkzbed"
    )


# Criação dos diretórios necessários se não existirem
os.makedirs(Config.TMP_DIR, exist_ok=True)
os.makedirs(Config.SECRETS_DIR, exist_ok=True)
