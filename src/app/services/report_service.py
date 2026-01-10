from io import BytesIO
from typing import Any, Dict, Optional
from docx import Document
from docx.text.paragraph import Paragraph
from docx.text.run import Run
from app.core.logger import get_logger
from config import Config
from lxml import etree # Importar lxml para manipulação direta de XML
import re # Importar re para usar finditer

logger = get_logger(__name__)

def replace_text_in_xml_element(xml_element, substitutions: Dict[str, str]):
    """
    Substitui placeholders em um elemento XML (e seus filhos) manipulando
    diretamente os nós de texto <w:t>. Lida com placeholders divididos em
    múltiplos <w:t> (split runs).
    """
    # Itera sobre as substituições
    for key, value in substitutions.items():
        # Encontra todas as ocorrências do placeholder no texto completo do elemento
        # Isso é feito concatenando o texto de todos os <w:t> e procurando a chave.
        # Depois, mapeamos a posição de volta para os nós <w:t>.
        
        # Coleta todos os nós <w:t> dentro do elemento atual
        text_nodes = xml_element.xpath(".//w:t")
        
        # Constrói um buffer de texto com o conteúdo de todos os nós
        full_text_buffer = ""
        for node in text_nodes:
            full_text_buffer += node.text if node.text is not None else ""

        # Encontra todas as ocorrências do placeholder no buffer
        # Usamos re.escape para garantir que caracteres especiais no key não quebrem o regex
        for match in reversed(list(re.finditer(re.escape(key), full_text_buffer))):
            start_match_index = match.start()
            end_match_index = match.end()
            
            # Encontra os nós <w:t> envolvidos na ocorrência atual
            nodes_involved = []
            current_pos_in_buffer = 0
            for node in text_nodes:
                node_text_len = len(node.text if node.text is not None else "")
                if current_pos_in_buffer + node_text_len > start_match_index and \
                   current_pos_in_buffer < end_match_index:
                    nodes_involved.append(node)
                current_pos_in_buffer += node_text_len
            
            if not nodes_involved:
                continue # Não deveria acontecer se o placeholder foi encontrado no buffer

            first_node = nodes_involved[0]
            last_node = nodes_involved[-1]

            # Calcula os offsets dentro do primeiro e último nó
            # Posição do início do placeholder dentro do texto do primeiro nó
            offset_in_first_node = start_match_index - (full_text_buffer.find(first_node.text) if first_node.text else 0)
            
            # Posição do fim do placeholder dentro do texto do último nó
            offset_in_last_node = end_match_index - (full_text_buffer.find(last_node.text) if last_node.text else 0)

            # Modifica o primeiro nó
            # O texto antes do placeholder no primeiro nó
            text_before_placeholder_in_first_node = first_node.text[:offset_in_first_node] if first_node.text else ""
            
            # O texto depois do placeholder no último nó
            text_after_placeholder_in_last_node = last_node.text[offset_in_last_node:] if last_node.text else ""

            first_node.text = text_before_placeholder_in_first_node + str(value) + text_after_placeholder_in_last_node
            
            # Limpa os nós intermediários e o restante do último nó (se ele não foi o primeiro nó)
            if first_node != last_node:
                for node in nodes_involved[1:]:
                    node.text = ""


def preencher_e_gerar_docx(
    dados: Dict[str, Any], caminho_template: str = Config.TEMPLATE_DOCX_PATH
) -> Optional[BytesIO]:
    try:
        document = Document(caminho_template)
        comps = dados.get("analise_competencias", {})

        # 1. Dicionário com AMBOS os formatos de placeholder
        substituicoes = {
            # Formato original para campos em caixas de texto e outros que funcionam
            "{{NOME_ALUNO}}": dados.get("nome_aluno", "Não identificado"),
            "{{TEMA}}": dados.get("tema_redacao", ""),
            "{{ANO}}": dados.get("ano_turma", ""),
            "{{BIMESTRE}}": dados.get("bimestre", ""),
            "{{NOTA_FINAL}}": str(dados.get("nota_final", 0)),
            "{{COMENTARIOS}}": dados.get("comentarios_gerais", ""),
            "{{ALERTA_ORIGINALIDADE}}": dados.get("alerta_originalidade") or ""
        }

        for i in range(1, 6):
            # Formato novo para competências (que davam problema de {})
            substituicoes[f"__NC{i}__"] = str(comps.get(f"c{i}", {}).get("nota", 0))
            substituicoes[f"__AC{i}__"] = comps.get(f"c{i}", {}).get("analise", "").replace("**", "")
            # Adiciona também o formato antigo para garantir (se o template não foi atualizado)
            substituicoes["{{NOTA_C{}}}".format(i)] = str(comps.get(f"c{i}", {}).get("nota", 0))
            substituicoes["{{ANALISE_C{}}}".format(i)] = comps.get(f"c{i}", {}).get("analise", "").replace("**", "")

        # --- ABORDAGEM UNIFICADA: Manipulação Direta de XML (para TUDO) ---
        # Aplica a substituição no corpo principal do documento
        replace_text_in_xml_element(document._element, substituicoes)

        # Aplica a substituição em todos os cabeçalhos e rodapés
        for section in document.sections:
            if section.header:
                replace_text_in_xml_element(section.header._element, substituicoes)
            if section.footer:
                replace_text_in_xml_element(section.footer._element, substituicoes)

        buffer = BytesIO()
        document.save(buffer)
        buffer.seek(0)
        logger.info(f"✅ Relatório preenchido para: {dados.get('nome_aluno')}")
        return buffer

    except Exception as e:
        logger.error(f"❌ Erro crítico no Word: {e}")
        return None
