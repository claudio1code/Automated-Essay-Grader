import json
import os
from typing import Any, Dict, Optional, TypedDict

import google.generativeai as genai
from PIL import Image

from app.core.logger import get_logger
from config import Config

logger = get_logger(__name__)


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
    Configura a autenticação usando a API KEY direta.
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            logger.warning(
                "GEMINI_API_KEY não encontrada. Tentando método legado (JSON)..."
            )
            cred_file = Config.GOOGLE_CREDENTIALS_PATH
            if os.path.exists(cred_file):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_file
            else:
                raise ValueError(
                    "Nenhuma chave de API ou arquivo de credenciais encontrado."
                )

        if api_key:
            genai.configure(api_key=api_key)

        logger.info("IA Configurada com sucesso (Método API Key).")

    except Exception as e:
        logger.error(f"Erro ao configurar a API: {e}")
        raise


def carregar_prompt(caminho_prompt: str = Config.PROMPT_PATH) -> str:
    """Carrega o prompt do arquivo."""
    with open(caminho_prompt, "r", encoding="utf-8") as f:
        return f.read()


def limpar_resposta_json(texto: str) -> str:
    """
    Remove markdown e outros caracteres indesejados da resposta da IA.
    """
    # Remove blocos de código markdown
    texto = texto.replace("```json", "").replace("```", "")
    # Remove espaços em branco no início e fim
    texto = texto.strip()
    return texto


def validar_e_corrigir_dados(dados: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida e corrige dados retornados pela IA.
    """
    # Garante que campos obrigatórios existam
    dados.setdefault("nome_aluno", "Não identificado")
    dados.setdefault("tema_redacao", "Não identificado")
    dados.setdefault("data_redacao", "Não identificado")
    dados.setdefault("comentarios_gerais", "")
    dados.setdefault("alerta_originalidade", None)
    dados.setdefault("analise_competencias", {})

    # Calcula nota_final se não existir ou estiver zerada
    comps = dados.get("analise_competencias", {})
    total = 0

    for i in range(1, 6):
        comp_key = f"c{i}"
        if comp_key not in comps:
            comps[comp_key] = {"nota": 0, "analise": "Análise não disponível."}

        # Garante que a competência tem nota e análise
        comp = comps[comp_key]
        comp.setdefault("nota", 0)
        comp.setdefault("analise", "Análise não disponível.")

        total += int(comp.get("nota", 0))

    # Atualiza ou define nota_final
    if dados.get("nota_final", 0) == 0:
        dados["nota_final"] = total

    return dados


def analisar_redacao(caminho_imagem: str, prompt: str) -> Optional[Dict[str, Any]]:
    """
    Analisa uma redação usando o Gemini Vision.
    Retorna um dicionário com os dados da correção.
    """
    try:
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.1,  # ← Mudou de 0.3 para 0.1 (mais determinístico)
            max_output_tokens=8000,
        )

        model = genai.GenerativeModel(
            model_name=Config.MODEL_NAME, generation_config=generation_config
        )

        if not os.path.exists(caminho_imagem):
            logger.error(f"Imagem não encontrada: {caminho_imagem}")
            return None

        logger.info(f"Carregando imagem: {caminho_imagem}")
        img = Image.open(caminho_imagem)

        logger.info("Enviando para a IA...")
        response = model.generate_content([prompt, img])

        if not response or not response.text:
            logger.error("IA retornou resposta vazia")
            return None

        # Log da resposta bruta
        logger.info("=" * 70)
        logger.info("RESPOSTA BRUTA DA IA:")
        logger.info(
            response.text[:500] + "..." if len(response.text) > 500 else response.text
        )
        logger.info("=" * 70)

        # Limpa e parseia o JSON
        texto_limpo = limpar_resposta_json(response.text)
        dados = json.loads(texto_limpo)

        # Valida e corrige os dados
        dados = validar_e_corrigir_dados(dados)

        # Log dos dados extraídos
        logger.info("Dados extraídos após validação:")
        logger.info(f"  - Nome: {dados.get('nome_aluno')}")
        logger.info(f"  - Tema: {dados.get('tema_redacao', '')[:50]}...")
        logger.info(f"  - Data: {dados.get('data_redacao')}")
        logger.info(f"  - Nota Final: {dados.get('nota_final')}")

        for i in range(1, 6):
            nota = dados["analise_competencias"].get(f"c{i}", {}).get("nota", 0)
            logger.info(f"  - C{i}: {nota} pontos")

        return dados

    except json.JSONDecodeError as e:
        logger.error(f"Erro ao parsear JSON da IA: {e}")
        # 'response' pode não estar definido se o erro ocorrer antes da atribuição
        response_text_for_log = (
            response.text if "response" in locals() and response else "N/A"
        )
        logger.error(
            f"Texto recebido: {response_text_for_log[:500] if response_text_for_log else 'N/A'}"
        )
        return None

    except Exception as e:
        logger.error(f"Erro na chamada da IA: {e}")
        import traceback

        logger.error(traceback.format_exc())
        return None
