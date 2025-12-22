import io
import os
from typing import Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from googleapiclient.http import MediaIoBaseUpload

from config import Config
from logger import get_logger

logger = get_logger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive"]


class GoogleDriveService:
    """
    Serviço responsável por todas as interações com a API do Google Drive.
    Encapsula autenticação, listagem, download e upload de arquivos.
    """

    def __init__(self):
        self.service = self._authenticate()

    def _authenticate(self) -> Resource:
        """
        Realiza a autenticação OAuth2 e retorna o cliente do Drive.
        """
        creds = None
        token_path = Config.DRIVE_TOKEN_PATH
        credentials_path = Config.DRIVE_CREDENTIALS_PATH

        # 1. Tenta carregar token existente
        if os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            except Exception as e:
                logger.warning(f"Token inválido ou corrompido: {e}")

        # 2. Se não válido, faz refresh ou novo login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Token de acesso atualizado via Refresh Token.")
                except Exception as e:
                    logger.warning(
                        f"Falha ao atualizar token: {e}. Solicitando novo login."
                    )
                    creds = None

            if not creds:
                if not os.path.exists(credentials_path):
                    msg = f"Credenciais OAuth não encontradas em: {credentials_path}"
                    logger.critical(msg)
                    raise FileNotFoundError(msg)

                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
                logger.info("Autenticação via navegador realizada com sucesso.")

            # 3. Salva o token atualizado
            with open(token_path, "w") as token:
                token.write(creds.to_json())

        return build("drive", "v3", credentials=creds)

    def list_pending_images(self, folder_id: str) -> List[Dict[str, str]]:
        """
        Lista arquivos de imagem (jpg/png) em uma pasta específica.
        Ignora arquivos na lixeira.
        """
        query = (
            f"'{folder_id}' in parents and "
            f"(mimeType='image/jpeg' or mimeType='image/png') and "
            f"trashed=false"
        )
        try:
            results = (
                self.service.files().list(q=query, fields="files(id, name)").execute()
            )
            items = results.get("files", [])
            return items
        except Exception as e:
            logger.error(f"Erro ao listar arquivos na pasta {folder_id}: {e}")
            return []

    def download_file(self, file_id: str) -> Optional[bytes]:
        """
        Faz o download do conteúdo de um arquivo e retorna em bytes.
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_data = request.execute()
            return file_data
        except Exception as e:
            logger.error(f"Erro ao baixar arquivo ID {file_id}: {e}")
            return None

    def upload_docx(
        self, file_buffer: io.BytesIO, file_name: str, folder_id: str
    ) -> Optional[str]:
        """
        Faz o upload de um arquivo .docx (memória) para uma pasta no Drive.
        Retorna o ID do novo arquivo.
        """
        try:
            file_metadata = {"name": file_name, "parents": [folder_id]}

            media = MediaIoBaseUpload(
                file_buffer,
                mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

            file = (
                self.service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )

            logger.info(f"Upload concluído: {file_name} (ID: {file.get('id')})")
            return file.get("id")

        except Exception as e:
            logger.error(f"Erro ao fazer upload do arquivo {file_name}: {e}")
            return None
