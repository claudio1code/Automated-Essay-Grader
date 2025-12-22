import os

import google.generativeai as genai

from config import Config
from logger import get_logger
from services import ai_service

logger = get_logger(__name__)


def verificar_integridade_api() -> bool:
    """
    Realiza um teste de fumaça (health check) na API do Gemini.
    Verifica se as credenciais estão carregadas e se o modelo responde.

    Returns:
        bool: True se o teste for bem-sucedido, False caso contrário.
    """
    logger.info("--- Iniciando diagnóstico da API Gemini ---")

    # 1. Verificação de Arquivo de Credenciais
    cred_path = Config.GOOGLE_CREDENTIALS_PATH
    if not os.path.exists(cred_path):
        logger.error(f"FALHA: Arquivo de credenciais não encontrado em: {cred_path}")
        logger.error(
            "Verifique se o arquivo está na pasta 'secrets/' e se o nome está correto no .env"
        )
        return False

    logger.info(f"OK: Arquivo de credenciais detectado: {cred_path}")

    # 2. Configuração da Lib via Service
    try:
        # Usamos o próprio serviço para configurar, garantindo que o teste reflete a realidade do app
        ai_service.configurar_ia()
        logger.info("OK: Biblioteca google-generativeai configurada via ai_service.")
    except Exception as e:
        logger.error(f"FALHA: Erro ao configurar biblioteca: {e}")
        return False

    # 3. Teste de Inferência
    model_name = Config.MODEL_NAME
    logger.info(f"Tentando conexão com o modelo: {model_name}...")

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            "Responda apenas com a palavra 'OK' se estiver me ouvindo."
        )

        if response and response.text:
            logger.info(f"SUCESSO: A IA respondeu: '{response.text.strip()}'")
            return True
        else:
            logger.warning("ALERTA: A IA não retornou texto (resposta vazia).")
            return False

    except Exception as e:
        logger.error(f"FALHA CRÍTICA na inferência: {e}")

        logger.info("Tentando listar modelos disponíveis para diagnóstico...")
        try:
            available_models = [
                m.name
                for m in genai.list_models()
                if "generateContent" in m.supported_generation_methods
            ]
            logger.info(
                f"Modelos disponíveis para geração de conteúdo: {available_models}"
            )
        except Exception as list_err:
            logger.error(f"Não foi possível listar os modelos: {list_err}")

        return False


if __name__ == "__main__":
    sucesso = verificar_integridade_api()
    if sucesso:
        print("\n✅ Diagnóstico concluído: O sistema está OPERACIONAL.")
    else:
        print("\n❌ Diagnóstico concluído: Ocorreram erros. Verifique os logs acima.")
