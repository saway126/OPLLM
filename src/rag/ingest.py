import os
import yaml
import logging
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# Load Config
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "settings.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ingest_documents():
    source_path = config["rag"]["document_source_path"]
    db_path = config["rag"]["chroma_db_path"]
    embedding_model_name = config["ollama"]["embedding_model"]
    base_url = config["ollama"]["base_url"]

    logger.info(f"Loading documents from {source_path}...")
    
    # Loaders for PDF and TXT
    loaders = [
        DirectoryLoader(source_path, glob="**/*.pdf", loader_cls=PyPDFLoader),
        DirectoryLoader(source_path, glob="**/*.txt", loader_cls=TextLoader),
    ]
    
    documents = []
    for loader in loaders:
        try:
            documents.extend(loader.load())
        except Exception as e:
            logger.error(f"Error loading documents: {e}")

    if not documents:
        logger.warning("No documents found.")
        return

    logger.info(f"Loaded {len(documents)} documents. Splitting...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config["rag"]["chunk_size"],
        chunk_overlap=config["rag"]["chunk_overlap"]
    )
    texts = text_splitter.split_documents(documents)
    
    logger.info(f"Created {len(texts)} chunks. Generating embeddings...")
    
    embeddings = OllamaEmbeddings(
        base_url=base_url,
        model=embedding_model_name
    )
    
    # Create or Update Vector DB
    vector_db = Chroma.from_documents(
        documents=texts,
        embedding=embeddings,
        persist_directory=db_path
    )
    vector_db.persist()
    logger.info(f"Successfully ingested documents into {db_path}")

if __name__ == "__main__":
    ingest_documents()
