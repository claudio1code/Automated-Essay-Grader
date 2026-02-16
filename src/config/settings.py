"""
Configurações centralizadas da aplicação.
Gerencia todas as variáveis de ambiente e configurações.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()


class Settings:
    """Classe central de configurações da aplicação."""
    
    # Configurações da Aplicação
    APP_NAME: str = "Corretor de Redação AI"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Configurações do Servidor
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8501"))
    
    # Configurações da IA
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "models/gemini-2.5-flash")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
    
    # Configurações de Temperatura e Geração
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.2"))
    MAX_OUTPUT_TOKENS: int = int(os.getenv("MAX_OUTPUT_TOKENS", "8000"))
    
    # Configurações de Arquivos
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ASSETS_DIR: str = os.path.join(BASE_DIR, "assets")
    SECRETS_DIR: str = os.path.join(BASE_DIR, "secrets")
    TMP_DIR: str = os.path.join(BASE_DIR, os.getenv("TMP_DIR", "tmp"))
    
    # Configurações de Banco de Dados
    VECTOR_DB_PATH: str = os.path.join(BASE_DIR, "data", "vector_db")
    REFERENCES_PATH: str = os.path.join(ASSETS_DIR, "referencias")
    
    # Configurações de Arquivos de Credenciais
    GOOGLE_CREDENTIALS_PATH: str = os.path.join(
        SECRETS_DIR, 
        os.getenv("GOOGLE_CREDENTIALS_FILE", "google-credentials.json")
    )
    DRIVE_CREDENTIALS_PATH: str = os.path.join(
        SECRETS_DIR, 
        os.getenv("DRIVE_CREDENTIALS_FILE", "credentials.json")
    )
    DRIVE_TOKEN_PATH: str = os.path.join(
        SECRETS_DIR, 
        os.getenv("DRIVE_TOKEN_FILE", "token.json")
    )
    
    # Configurações de Templates
    TEMPLATE_DOCX_PATH: str = os.path.join(
        ASSETS_DIR, 
        os.getenv("TEMPLATE_DOCX_FILE", "template.docx")
    )
    PROMPT_PATH: str = os.path.join(
        ASSETS_DIR, 
        os.getenv("PROMPT_FILE", "prompt.txt")
    )
    
    # Configurações de Upload
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    ALLOWED_IMAGE_EXTENSIONS: list = [
        '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'
    ]
    
    # Configurações de Google Drive
    DRIVE_FOLDER_INPUT_ID: str = os.getenv(
        "DRIVE_FOLDER_INPUT_ID", 
        "1c_8ybbo6HAhMxlOeNKX71PPF8TfySKx-"
    )
    DRIVE_FOLDER_OUTPUT_ID: str = os.getenv(
        "DRIVE_FOLDER_OUTPUT_ID", 
        "16xRIPkBY8gRp9vNzxgH1Ex4GhTnkzbed"
    )
    
    # Configurações de Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    
    # Configurações de Cache
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "true").lower() == "true"
    
    # Configurações de Segurança
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALLOWED_HOSTS: list = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    
    # Configurações de Performance
    MAX_CONCURRENT_ANALYSES: int = int(os.getenv("MAX_CONCURRENT_ANALYSES", "5"))
    ANALYSIS_TIMEOUT_SECONDS: int = int(os.getenv("ANALYSIS_TIMEOUT_SECONDS", "300"))
    
    @classmethod
    def validate(cls) -> bool:
        """Valida configurações essenciais."""
        errors = []
        
        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY não configurada")
        
        if not os.path.exists(cls.ASSETS_DIR):
            errors.append(f"Diretório assets não encontrado: {cls.ASSETS_DIR}")
        
        if not os.path.exists(cls.PROMPT_PATH):
            errors.append(f"Arquivo de prompt não encontrado: {cls.PROMPT_PATH}")
        
        if errors:
            raise ValueError(f"Configurações inválidas: {'; '.join(errors)}")
        
        return True
    
    @classmethod
    def create_directories(cls) -> None:
        """Cria diretórios necessários."""
        directories = [
            cls.TMP_DIR,
            cls.SECRETS_DIR,
            cls.VECTOR_DB_PATH,
            cls.REFERENCES_PATH
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def get_database_url(cls) -> str:
        """Retorna URL do banco de dados."""
        return f"file://{cls.VECTOR_DB_PATH}"
    
    @classmethod
    def is_production(cls) -> bool:
        """Verifica se está em ambiente de produção."""
        return not cls.DEBUG and cls.HOST != "localhost"
    
    @classmethod
    def get_cors_origins(cls) -> list:
        """Retorna origins permitidos para CORS."""
        if cls.is_production():
            return cls.ALLOWED_HOSTS
        return ["http://localhost:8501", "http://127.0.0.1:8501"]


# Instância global de configurações
settings = Settings()

# Valida e cria diretórios na importação
try:
    settings.validate()
    settings.create_directories()
except Exception as e:
    print(f"Erro na configuração: {e}")
    # Em ambiente de desenvolvimento, continua mesmo com erro
    if not settings.DEBUG:
        raise
