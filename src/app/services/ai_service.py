"""
Serviço de IA aprimorado com tratamento robusto de erros.
Centraliza e melhora as operações com modelos de linguagem.
"""

import json
import os
from typing import Any, Dict, Optional, TypedDict
from PIL import Image

import google.generativeai as genai

from app.core.logger import get_logger
from app.core.exceptions import IAException, ValidationException
from app.core.validators import TextValidator
from app.core.utils import TextUtils
from app.services.vector_service import VectorService
from config.settings import settings

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


class EnhancedAIService:
    """Serviço de IA com tratamento robusto de erros e logging."""
    
    def __init__(self):
        self.model = None
        self.vector_service = None
        self._initialized = False
    
    def _ensure_initialized(self) -> None:
        """Garante que o serviço está inicializado."""
        if not self._initialized:
            self.configurar_ia()
    
    def configurar_ia(self) -> None:
        """
        Configura a autenticação usando a API KEY direta.
        """
        try:
            api_key = os.getenv("GEMINI_API_KEY")

            if not api_key:
                logger.warning("GEMINI_API_KEY não encontrada. Tentando método legado...")
                cred_file = settings.GOOGLE_CREDENTIALS_PATH
                if os.path.exists(cred_file):
                    genai.configure(credentials_path=cred_file)
                    logger.info("IA Configurada com sucesso (Método JSON).")
                else:
                    raise IAException("Nenhuma credencial encontrada (API Key ou JSON)")
            else:
                genai.configure(api_key=api_key)
                logger.info("IA Configurada com sucesso (Método API Key).")

            # Configura o modelo
            generation_config = genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.2,
                max_output_tokens=8000,
            )

            self.model = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL_NAME, 
                generation_config=generation_config
            )
            
            self._initialized = True
            logger.info(f"Modelo {settings.GEMINI_MODEL_NAME} configurado com sucesso")

        except Exception as e:
            logger.error(f"Erro ao configurar IA: {str(e)}")
            raise IAException(f"Falha na configuração da IA: {str(e)}")
    
    def carregar_prompt(self) -> str:
        """
        Carrega o prompt mestre do arquivo.
        """
        try:
            if not os.path.exists(settings.PROMPT_PATH):
                raise IAException(f"Arquivo de prompt não encontrado: {settings.PROMPT_PATH}")

            with open(settings.PROMPT_PATH, "r", encoding="utf-8") as f:
                prompt = f.read()

            if not prompt.strip():
                raise IAException("O arquivo de prompt está vazio")

            logger.info("Prompt carregado com sucesso")
            return prompt

        except Exception as e:
            logger.error(f"Erro ao carregar prompt: {str(e)}")
            raise IAException(f"Falha ao carregar prompt: {str(e)}")
    
    def analisar_redacao(self, caminho_imagem: str, prompt: str, tema_redacao: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Analisa uma redação usando o Gemini Vision com tratamento robusto de erros.
        """
        try:
            self._ensure_initialized()
            
            # Validações
            if not os.path.exists(caminho_imagem):
                raise ValidationException(f"Imagem não encontrada: {caminho_imagem}")
            
            if not prompt or not prompt.strip():
                raise ValidationException("Prompt não fornecido")
            
            # Busca referências RAG
            referencias_encontradas = self._buscar_referencias(tema_redacao)
            
            # Prepara prompt com referências
            prompt_com_referencias = prompt.replace("{{REFERENCIAS}}", referencias_encontradas)
            
            # Carrega e valida imagem
            imagem = self._carregar_imagem(caminho_imagem)
            
            # Realiza análise
            resultado = self._realizar_analise(imagem, prompt_com_referencias)
            
            # Valida e processa resultado
            resultado_processado = self._processar_resultado(resultado)
            
            logger.info("Análise da redação concluída com sucesso")
            return resultado_processado

        except ValidationException as e:
            logger.warning(f"Erro de validação na análise: {str(e)}")
            raise
        except IAException as e:
            logger.error(f"Erro de IA na análise: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado na análise: {str(e)}")
            raise IAException(f"Falha na análise da redação: {str(e)}")
    
    def _buscar_referencias(self, tema_redacao: Optional[str]) -> str:
        """Busca referências usando RAG."""
        if not tema_redacao:
            logger.info("Tema não fornecido - RAG não será utilizado")
            return ""
        
        try:
            if not self.vector_service:
                self.vector_service = VectorService()
            
            docs_referencia = self.vector_service.buscar_referencias(tema_redacao)
            
            if docs_referencia:
                referencias = "\n\n### Referências para este tema:\n" + "\n---\n".join(docs_referencia)
                logger.info(f"Referências RAG injetadas: {len(docs_referencia)} documentos")
                return referencias
            else:
                logger.info("Nenhuma referência encontrada para o tema")
                return ""
                
        except Exception as e:
            logger.warning(f"Erro ao buscar referências: {str(e)}")
            return ""
    
    def _carregar_imagem(self, caminho_imagem: str) -> Image.Image:
        """Carrega e valida a imagem."""
        try:
            imagem = Image.open(caminho_imagem)
            
            # Validações básicas
            if imagem.mode not in ['RGB', 'RGBA', 'L']:
                logger.warning(f"Modo de imagem incomum: {imagem.mode}")
                imagem = imagem.convert('RGB')
            
            # Limita tamanho para evitar problemas
            max_dimension = 4096
            if max(imagem.width, imagem.height) > max_dimension:
                imagem.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                logger.info(f"Imagem redimensionada para {imagem.width}x{imagem.height}")
            
            return imagem
            
        except Exception as e:
            raise IAException(f"Erro ao carregar imagem: {str(e)}")
    
    def _realizar_analise(self, imagem: Image.Image, prompt: str) -> Dict[str, Any]:
        """Realiza a análise com o modelo Gemini."""
        try:
            response = self.model.generate_content([prompt, imagem])
            
            if not response.text:
                raise IAException("Resposta vazia do modelo")
            
            # Tenta fazer parse do JSON
            try:
                resultado = json.loads(response.text)
                return resultado
            except json.JSONDecodeError as e:
                logger.error(f"JSON inválido retornado pelo modelo: {str(e)}")
                logger.debug(f"Resposta bruta: {response.text[:500]}...")
                raise IAException("Resposta do modelo não está em formato JSON válido")
                
        except Exception as e:
            if "quota" in str(e).lower():
                raise IAException("Cota da API excedida. Tente novamente mais tarde.")
            elif "rate" in str(e).lower():
                raise IAException("Muitas requisições. Aguarde um momento e tente novamente.")
            else:
                raise IAException(f"Erro na chamada da API: {str(e)}")
    
    def _processar_resultado(self, resultado: Dict[str, Any]) -> Dict[str, Any]:
        """Processa e valida o resultado da análise."""
        try:
            # Garante estrutura mínima
            resultado_padronizado = self._garantir_estrutura(resultado)
            
            # Valida notas
            self._validar_notas(resultado_padronizado)
            
            # Adiciona metadados
            resultado_padronizado["data_analise"] = TextUtils.clean_text(str(os.path.getctime(__file__)))
            
            return resultado_padronizado
            
        except Exception as e:
            logger.error(f"Erro ao processar resultado: {str(e)}")
            raise IAException(f"Erro no processamento do resultado: {str(e)}")
    
    def _garantir_estrutura(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Garante que o resultado tem a estrutura esperada."""
        estrutura_padrao = {
            "nome_aluno": dados.get("nome_aluno", ""),
            "tema_redacao": dados.get("tema_redacao", ""),
            "data_redacao": dados.get("data_redacao", ""),
            "nota_final": dados.get("nota_final", 0),
            "comentarios_gerais": dados.get("comentarios_gerais", ""),
            "alerta_originalidade": dados.get("alerta_originalidade"),
            "analise_competencias": dados.get("analise_competencias", {})
        }
        
        # Garante competências
        comps = estrutura_padrao["analise_competencias"]
        for i in range(1, 6):
            comp_key = f"c{i}"
            if comp_key not in comps:
                comps[comp_key] = {"nota": 0, "analise": "Análise não disponível."}
            
            # Garante estrutura da competência
            comp = comps[comp_key]
            comp.setdefault("nota", 0)
            comp.setdefault("analise", "Análise não disponível.")
        
        return estrutura_padrao
    
    def _validar_notas(self, resultado: Dict[str, Any]) -> None:
        """Valida as notas das competências."""
        competencias = resultado.get("analise_competencias", {})
        
        total = 0
        for comp_key, comp_data in competencias.items():
            if comp_key.startswith('c'):
                nota = comp_data.get("nota", 0)
                
                if not isinstance(nota, (int, float)):
                    logger.warning(f"Nota inválida em {comp_key}: {nota}")
                    comp_data["nota"] = 0
                    nota = 0
                
                if nota < 0 or nota > 200:
                    logger.warning(f"Nota fora do intervalo em {comp_key}: {nota}")
                    comp_data["nota"] = max(0, min(200, nota))
                    nota = comp_data["nota"]
                
                total += int(nota)
        
        # Atualiza nota final se necessário
        if resultado.get("nota_final", 0) == 0:
            resultado["nota_final"] = total
        
        logger.info(f"Nota final calculada: {total}")


# Instância global para uso na aplicação
ai_service_instance = EnhancedAIService()

# Para compatibilidade, criar alias e expor funções
ai_service = ai_service_instance

# Expor funções para compatibilidade
configurar_ia = ai_service_instance.configurar_ia
carregar_prompt = ai_service_instance.carregar_prompt
analisar_redacao = ai_service_instance.analisar_redacao
