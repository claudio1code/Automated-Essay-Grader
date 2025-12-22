import json
import os
from typing import Any, Dict, Optional, TypedDict

import google.generativeai as genai
from PIL import Image

from config import Config
from logger import get_logger

logger = get_logger(__name__)


# --- Definição do Schema de Resposta (Tipagem Forte) ---
class DetalheCompetencia(TypedDict):
    nota: int
    analise: str


class AnaliseCompetencias(TypedDict):
    c1: DetalheCompetencia
    c2: DetalheCompetencia
    c3: DetalheCompetencia
    c4: DetalheCompetencia
    c5: DetalheCompetencia


class CorrecaoRedacao(TypedDict):
    nome_aluno: str
    tema_redacao: str
    data_redacao: str
    nota_final: int
    comentarios_gerais: str
    alerta_originalidade: Optional[str]
    analise_competencias: AnaliseCompetencias


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
    Utiliza o recurso 'response_schema' do Gemini para garantir JSON válido.

    Args:
        caminho_imagem (str): Caminho do arquivo da imagem da redação.
        prompt (str): O prompt de instruções para a IA.

    Returns:
        Optional[Dict[str, Any]]: Um dicionário com os dados da correção ou None em caso de falha.
    """
    model_name = Config.MODEL_NAME
    logger.info(f"Iniciando análise estruturada com o modelo: {model_name}")

    try:
        # Configuração de Geração para forçar JSON seguindo o Schema
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json", response_schema=CorrecaoRedacao
        )

        model = genai.GenerativeModel(
            model_name=model_name, generation_config=generation_config
        )

        # Carrega a imagem
        if not os.path.exists(caminho_imagem):
            logger.error(f"A imagem não foi encontrada em '{caminho_imagem}'")
            return None

        img = Image.open(caminho_imagem)

        # Gera o conteúdo
        # Prompt Adicional para reforçar a obediência ao Schema
        prompt_reforco = (
            f"{prompt}\n\n"
            "IMPORTANTE: Responda APENAS com o JSON estrito seguindo a estrutura fornecida."
        )

        response = model.generate_content([prompt_reforco, img])
        resposta_texto = response.text

        # Parse direto do JSON (agora garantido pela API)
        try:
            dados_redacao = json.loads(resposta_texto)
            logger.info("Análise concluída e JSON estruturado recebido com sucesso.")
            return dados_redacao

        except json.JSONDecodeError as json_err:
            logger.error(
                f"Falha ao decodificar JSON (mesmo com schema forçado): {json_err}"
            )
            logger.debug(f"Conteúdo recebido: {resposta_texto}")
            return None

    except Exception as e:
        logger.error(f"Ocorreu um erro na chamada da API Gemini: {e}")
        return None
