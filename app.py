import os

import streamlit as st

from config import Config
from logger import get_logger
from services import ai_service, report_service

# --- Configuração de Logs ---
logger = get_logger(__name__)

# --- Configuração da Página e Inicialização ---
st.set_page_config(layout="wide", page_title="Projeto Mae Redação", page_icon="✍️")

st.title("✍️ Projeto Mae Redação")
st.markdown(
    "Faça o upload da foto de uma redação manuscrita para receber uma análise completa e precisa."
)
st.divider()

# --- Inicialização do Sistema (IA e Configurações) ---
try:
    # Configura a API do Gemini
    ai_service.configurar_ia()

    # Carrega o prompt (usando cache de sessão se possível)
    if "prompt_mestre" not in st.session_state:
        st.session_state["prompt_mestre"] = ai_service.carregar_prompt()
        logger.info("Prompt carregado e armazenado na sessão.")

    PROMPT_MESTRE = st.session_state["prompt_mestre"]

except Exception as e:
    logger.critical(f"Erro Crítico na Inicialização: {e}")
    st.error(f"Erro Crítico na Inicialização do Sistema: {e}")
    st.stop()

# --- Interface do Usuário ---
imagem_redacao = st.file_uploader(
    "Envie a foto da redação aqui (formato .jpg ou .png)", type=["jpg", "png", "jpeg"]
)

if imagem_redacao is not None:
    # Utiliza o diretório temporário definido na configuração
    temp_dir = Config.TEMP_UPLOADS_DIR

    # Define o caminho completo
    caminho_imagem_temp = os.path.join(temp_dir, imagem_redacao.name)

    try:
        with open(caminho_imagem_temp, "wb") as f:
            f.write(imagem_redacao.getbuffer())
        logger.info(f"Imagem recebida e salva em: {caminho_imagem_temp}")
    except Exception as e:
        logger.error(f"Falha ao salvar imagem temporária: {e}")
        st.error("Falha ao processar o upload da imagem.")
        st.stop()

    if st.button("Analisar Redação com IA", type="primary", use_container_width=True):
        dados_redacao = None

        with st.spinner("Analisando a imagem e corrigindo a redação..."):
            try:
                dados_redacao = ai_service.analisar_redacao(
                    caminho_imagem_temp, PROMPT_MESTRE
                )
            except Exception as e:
                logger.error(f"Exceção não tratada durante a análise: {e}")
                st.error("Ocorreu um erro inesperado durante a análise.")

        # Tenta remover o arquivo temporário após o uso
        try:
            if os.path.exists(caminho_imagem_temp):
                os.remove(caminho_imagem_temp)
                logger.info(f"Arquivo temporário removido: {caminho_imagem_temp}")
        except OSError as e:
            logger.warning(f"Não foi possível remover o arquivo temporário: {e}")

        if dados_redacao:
            st.success("Análise concluída com sucesso!", icon="🎉")

            nome_aluno = dados_redacao.get("nome_aluno", "Aluno")
            st.subheader(f"Análise para: {nome_aluno}")

            # Exibição dos dados principais
            st.write(f"**Tema:** {dados_redacao.get('tema_redacao', 'N/A')}")
            st.write(
                f"**Nota Final Estimada:** {dados_redacao.get('nota_final', 'N/A')}"
            )

            with st.expander("Ver Comentários Gerais"):
                st.markdown(dados_redacao.get("comentarios_gerais", ""))

            # Geração do Arquivo DOCX
            try:
                arquivo_docx_bytes = report_service.preencher_e_gerar_docx(
                    dados_redacao
                )

                if arquivo_docx_bytes:
                    nome_aluno_formatado = nome_aluno.replace(" ", "_")
                    nome_arquivo_final = f"Correcao_{nome_aluno_formatado}.docx"

                    st.download_button(
                        label=f"📥 Baixar Relatório Completo (.docx)",
                        data=arquivo_docx_bytes,
                        file_name=nome_arquivo_final,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )
                else:
                    st.error(
                        "Ocorreu um erro ao gerar o arquivo .docx. Tente novamente."
                    )
            except Exception as e:
                logger.error(f"Erro ao preparar download: {e}")
                st.error("Erro ao preparar o arquivo para download.")
        else:
            st.error(
                "Não foi possível analisar a redação. Verifique a qualidade da imagem ou a resposta da IA nos logs."
            )
