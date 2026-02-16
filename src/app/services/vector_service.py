import os
from typing import List

import chromadb
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config.settings import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class VectorService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.vector_db_path = settings.VECTOR_DB_PATH
        self.references_path = settings.REFERENCES_PATH
        # Certifica-se de que o diretório de referências existe antes de tentar carregar
        os.makedirs(self.references_path, exist_ok=True)
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        self.chroma_client = chromadb.PersistentClient(path=self.vector_db_path)
        self.collection_name = "referencias_professora_elaine"

        # Tenta obter a coleção existente ou cria uma nova
        try:
            self.vector_store = Chroma(
                client=self.chroma_client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
            )
            # Verifica se a coleção já existe e tem conteúdo.
            # No ChromaDB, a contagem de documentos é feita diretamente na coleção.
            if self.vector_store._collection.count() == 0:
                logger.info("Coleção vazia ou não existente. Indexando documentos...")
                self.indexar_documentos()
            else:
                logger.info("Vector DB já inicializado com documentos existentes.")
        except Exception as e:
            # Isso pode acontecer se a coleção não existir de forma alguma, ou outros erros.
            logger.warning(f"Erro ao carregar coleção '{self.collection_name}': {e}. Tentando criar e indexar.")
            self.indexar_documentos()


    def indexar_documentos(self):
        documents = []
        for root, _, files in os.walk(self.references_path):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith(".docx"):
                    logger.info(f"Carregando arquivo DOCX: {file_path}")
                    loader = Docx2txtLoader(file_path)
                    documents.extend(loader.load())
                elif file.endswith(".pdf"):
                    logger.info(f"Carregando arquivo PDF: {file_path}")
                    loader = PyPDFLoader(file_path)
                    documents.extend(loader.load())

        if documents:
            logger.info(f"Indexando {len(documents)} documentos no ChromaDB...")
            # Remove a coleção existente se houver, para garantir uma indexação limpa
            try:
                self.chroma_client.delete_collection(name=self.collection_name)
                logger.info(f"Coleção '{self.collection_name}' existente foi removida para reindexação.")
            except Exception as e:
                logger.debug(f"Coleção '{self.collection_name}' não existia para ser removida ou erro: {e}")

            self.vector_store = Chroma.from_documents(
                documents,
                self.embeddings,
                client=self.chroma_client,
                collection_name=self.collection_name,
            )
            logger.info("Documentos indexados com sucesso.")
        else:
            logger.warning("Nenhum documento .docx ou .pdf encontrado para indexar.")
            # Garante que uma coleção vazia ainda seja inicializada
            self.vector_store = Chroma(
                client=self.chroma_client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
            )


    def buscar_referencias(self, tema: str) -> List[str]:
        if not tema:
            logger.warning("Tema vazio fornecido para buscar referências.")
            return []

        try:
            # Busca os 2 documentos mais similares ao tema
            docs = self.vector_store.similarity_search(tema, k=2)
            logger.info(f"Encontradas {len(docs)} referências para o tema: '{tema}'")
            return [doc.page_content for doc in docs]
        except Exception as e:
            logger.error(f"Erro ao buscar referências no Vector DB para o tema '{tema}': {e}")
            return []
