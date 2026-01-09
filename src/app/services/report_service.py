from io import BytesIO
from typing import Any, Dict, Optional

from docx import Document
from docx.text.paragraph import Paragraph

from app.core.logger import get_logger
from config import Config

logger = get_logger(__name__)


def paragraph_replace_text(paragraph: Paragraph, substituicoes: Dict[str, str]):
    """
    Substitui placeholders em um parágrafo, tratando a fragmentação de 'runs'
    que ocorre frequentemente em templates Word.
    """
    # Verificação rápida para evitar processamento se não houver placeholders
    if "{{" not in paragraph.text and "__" not in paragraph.text:
        return

    for key, value in substituicoes.items():
        if key not in paragraph.text:
            continue

        # Tenta substituir nos runs individualmente (preserva formatação se o placeholder estiver inteiro num run)
        for run in paragraph.runs:
            if key in run.text:
                run.text = run.text.replace(key, str(value))

        # Se após tentar nos runs a chave ainda persistir no parágrafo (fragmentação entre runs)
        if key in paragraph.text:
            # Estratégia de reconstrução: encontra o texto, substitui e limpa runs excedentes
            full_text = "".join(run.text for run in paragraph.runs)
            new_text = full_text.replace(key, str(value))

            if len(paragraph.runs) > 0:
                # Mantém o primeiro run para preservar o estilo base e limpa os outros
                paragraph.runs[0].text = new_text
                for i in range(1, len(paragraph.runs)):
                    paragraph.runs[i].text = ""


def preencher_e_gerar_docx(
    dados: Dict[str, Any], caminho_template: str = Config.TEMPLATE_DOCX_PATH
) -> Optional[BytesIO]:
    """
    Gera o relatório corrigido preenchendo o template Word.
    Suporta placeholders em parágrafos, tabelas, cabeçalhos, rodapés e caixas de texto.
    """
    try:
        document = Document(caminho_template)
        comps = dados.get("analise_competencias", {})

        # Dicionário de substituições unificado
        substituicoes = {
            "{{NOME_ALUNO}}": dados.get("nome_aluno", "Não identificado"),
            "{{TEMA}}": dados.get("tema_redacao", ""),
            "{{ANO}}": dados.get("ano_turma", ""),
            "{{BIMESTRE}}": dados.get("bimestre", ""),
            "{{NOTA_FINAL}}": str(dados.get("nota_final", 0)),
            "{{COMENTARIOS}}": dados.get("comentarios_gerais", ""),
            "{{ALERTA_ORIGINALIDADE}}": dados.get("alerta_originalidade") or "",
        }

        # Adiciona competências em múltiplos formatos de placeholder para compatibilidade
        for i in range(1, 6):
            nota = str(comps.get(f"c{i}", {}).get("nota", 0))
            analise = comps.get(f"c{i}", {}).get("analise", "").replace("**", "")

            # Formato 1: __NC1__ / __AC1__ (Mais seguro para caixas de texto)
            substituicoes[f"__NC{i}__"] = nota
            substituicoes[f"__AC{i}__"] = analise

            # Formato 2: {{NOTA_C1}} / {{ANALISE_C1}} (Padrão)
            substituicoes["{{NOTA_C" + str(i) + "}}"] = nota
            substituicoes["{{ANALISE_C" + str(i) + "}}"] = analise

        # --- 1. Processamento de todas as estruturas padrão ---

        # Parágrafos do corpo
        for p in document.paragraphs:
            paragraph_replace_text(p, substituicoes)

        # Tabelas (corpo, cabeçalhos e rodapés)
        def processar_tabelas(tabelas):
            for table in tabelas:
                for row in table.rows:
                    for cell in row.cells:
                        for p in cell.paragraphs:
                            paragraph_replace_text(p, substituicoes)

        processar_tabelas(document.tables)

        # Cabeçalhos e Rodapés
        for section in document.sections:
            for p in section.header.paragraphs:
                paragraph_replace_text(p, substituicoes)
            processar_tabelas(section.header.tables)

            for p in section.footer.paragraphs:
                paragraph_replace_text(p, substituicoes)
            processar_tabelas(section.footer.tables)

        # --- 2. Processamento Profundo via XPath (Para Caixas de Texto e Shapes) ---
        # No Word, caixas de texto são frequentemente armazenadas em elementos v:shape
        # ou dentro de blocos w:drawing que não são mapeados diretamente para a lista de parágrafos.
        # Varremos todos os elementos de texto (w:t) no XML.

        for element in document._element.xpath(".//w:t"):
            if element.text:
                for key, value in substituicoes.items():
                    if key in element.text:
                        element.text = element.text.replace(key, str(value))

        # --- 3. Finalização ---
        buffer = BytesIO()
        document.save(buffer)
        buffer.seek(0)

        logger.info(f"✅ Relatório DOCX gerado com sucesso: {dados.get('nome_aluno')}")
        return buffer

    except Exception as e:
        logger.error(f"❌ Erro ao preencher template DOCX: {e}")
        import traceback

        logger.error(traceback.format_exc())
        return None
