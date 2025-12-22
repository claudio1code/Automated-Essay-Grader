import os

from config import Config
from logger import get_logger
from services import ai_service, report_service
from services.drive_service import GoogleDriveService

# --- Configuração de Logs ---
logger = get_logger(__name__)


def main():
    logger.info("Iniciando assistente de correção em lote...")

    # Garante que o diretório temporário exista
    os.makedirs(Config.TEMP_LOTE_DIR, exist_ok=True)

    try:
        # --- 1. CONFIGURAÇÃO INICIAL ---
        ai_service.configurar_ia()

        # Inicializa o serviço do Drive (já trata autenticação internamente)
        drive_service = GoogleDriveService()
        logger.info("Serviços de IA e Google Drive inicializados.")

        prompt_mestre = ai_service.carregar_prompt()
        logger.info("Prompt da IA carregado.")

        # --- 2. BUSCA DE ARQUIVOS ---
        folder_input_id = Config.DRIVE_FOLDER_INPUT_ID
        items = drive_service.list_pending_images(folder_input_id)

        if not items:
            logger.info(
                "Nenhuma nova redação encontrada para corrigir na pasta de entrada."
            )
            return

        logger.info(f"Encontradas {len(items)} redações para corrigir.")

        # --- 3. PROCESSAMENTO ---
        for item in items:
            file_id = item["id"]
            file_name = item["name"]

            logger.info(f"--- Processando: {file_name} (ID: {file_id}) ---")

            caminho_imagem_temp = os.path.join(Config.TEMP_LOTE_DIR, file_name)

            try:
                # Download da imagem (em bytes)
                file_content = drive_service.download_file(file_id)

                if not file_content:
                    logger.warning(f"Falha ao baixar o arquivo '{file_name}'. Pulando.")
                    continue

                # Salva temporariamente para a IA processar
                # (O ai_service atualmente espera um caminho de arquivo)
                with open(caminho_imagem_temp, "wb") as f:
                    f.write(file_content)

                # Análise da IA
                dados_redacao = ai_service.analisar_redacao(
                    caminho_imagem_temp, prompt_mestre
                )

                if not dados_redacao:
                    logger.warning(
                        f"Falha na análise da IA para o arquivo '{file_name}'. Pulando."
                    )
                    continue

                # Geração do DOCX
                arquivo_docx_bytes = report_service.preencher_e_gerar_docx(
                    dados_redacao
                )

                if not arquivo_docx_bytes:
                    logger.warning(
                        f"Falha ao gerar o arquivo .docx para '{file_name}'. Pulando."
                    )
                    continue

                # Upload do Resultado
                nome_aluno = (
                    dados_redacao.get("nome_aluno", "Aluno").strip().replace(" ", "_")
                )
                # Adiciona parte do ID para garantir unicidade
                nome_arquivo_final = f"Correcao_{nome_aluno}_{file_id[:4]}.docx"

                folder_output_id = Config.DRIVE_FOLDER_OUTPUT_ID

                novo_id = drive_service.upload_docx(
                    arquivo_docx_bytes, nome_arquivo_final, folder_output_id
                )

                if novo_id:
                    logger.info(f"Sucesso! Relatório salvo. ID: {novo_id}")
                else:
                    logger.error(
                        f"Falha ao fazer upload do relatório para '{file_name}'."
                    )

            except Exception as e:
                logger.error(f"Erro ao processar o arquivo '{file_name}': {e}")

            finally:
                # Limpeza do arquivo temporário
                if os.path.exists(caminho_imagem_temp):
                    try:
                        os.remove(caminho_imagem_temp)
                    except OSError:
                        pass

    except Exception as e:
        logger.critical(f"Ocorreu um erro fatal na execução do script: {e}")


if __name__ == "__main__":
    main()
