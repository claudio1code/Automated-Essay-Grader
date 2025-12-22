import json
import os
import re
from typing import Any, Dict, Optional

import google.generativeai as genai
from PIL import Image

from config import Config
from logger import get_logger

logger = get_logger(__name__)


def configurar_ia() -> None:
    """
    Configura a autenticação da API do Google Gemini.
    Define a variável de ambiente para as credenciais e configura o transporte.
    """
    try:
        credentials_path = Config.GOOGLE_CREDENTIALS_PATH
        if not os.path.exists(credentials_path):
            msg = f"ERRO CRÍTICO: O arquivo de credenciais '{credentials_path}' não foi encontrado."
            logger.critical(msg)
            raise FileNotFoundError(msg)

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        genai.configure(transport="rest")
        logger.info("API Gemini configurada com sucesso.")

    except Exception as e:
        logger.error(f"Erro ao configurar a API: {e}")
        raise


def carregar_prompt(caminho_prompt: str = Config.PROMPT_PATH) -> str:
    """
    Carrega o conteúdo do arquivo de prompt.

    Args:
        caminho_prompt (str): Caminho para o arquivo de texto contendo o prompt.

    Returns:
        str: O conteúdo do prompt.
    """
    try:
        with open(caminho_prompt, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        msg = (
            f"ERRO CRÍTICO: O arquivo de prompt '{caminho_prompt}' não foi encontrado."
        )
        logger.critical(msg)
        raise
    except Exception as e:
        logger.error(f"Erro ao ler o arquivo de prompt: {e}")
        raise


def analisar_redacao(caminho_imagem: str, prompt: str) -> Optional[Dict[str, Any]]:
    """
    Envia a imagem para a IA e retorna a análise estruturada.

    Args:
        caminho_imagem (str): Caminho do arquivo da imagem da redação.
        prompt (str): O prompt de instruções para a IA.

    Returns:
        Optional[Dict[str, Any]]: Um dicionário com os dados da correção ou None em caso de falha.
    """
    model_name = Config.MODEL_NAME
    logger.info(f"Iniciando análise com o modelo: {model_name}")

    try:
        # Inicializa o modelo
        model = genai.GenerativeModel(model_name)

        # Carrega a imagem
        if not os.path.exists(caminho_imagem):
            logger.error(f"A imagem não foi encontrada em '{caminho_imagem}'")
            return None

        img = Image.open(caminho_imagem)

        # Gera o conteúdo
        response = model.generate_content([prompt, img])
        resposta_texto = response.text

        # Extrai o JSON da resposta
        json_match = re.search(r"\{.*\}", resposta_texto, re.DOTALL)

        if json_match:
            json_str = json_match.group(0)
            try:
                dados_redacao = json.loads(json_str)
                logger.info("Análise concluída e JSON processado com sucesso.")
                return dados_redacao
            except json.JSONDecodeError:
                logger.error(
                    f"A IA retornou um JSON inválido. Resposta recebida:\n{json_str}"
                )
                return None
        else:
            logger.error(
                f"Nenhuma estrutura JSON foi encontrada na resposta da IA. Resposta recebida:\n{resposta_texto}"
            )
            return None

    except Exception as e:
        logger.error(f"Ocorreu um erro na chamada da API Gemini: {e}")
        return None
