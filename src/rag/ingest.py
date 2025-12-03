import os
import yaml
import logging
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

# Load Config
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "settings.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ingest_documents():
    source_path = config["rag"]["document_source_path"]
    db_path = config["rag"]["chroma_db_path"] # We use the same config key for path
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
    
    # Create or Update Vector DB (FAISS)
    if os.path.exists(db_path) and os.path.exists(os.path.join(db_path, "index.faiss")):
        logger.info("Loading existing FAISS index...")
        try:
            vector_db = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
            vector_db.add_documents(texts)
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}. Creating new one.")
            vector_db = FAISS.from_documents(documents=texts, embedding=embeddings)
    else:
        logger.info("Creating new FAISS index...")
        vector_db = FAISS.from_documents(
            documents=texts,
            embedding=embeddings
        )
    
    vector_db.save_local(db_path)
    logger.info(f"Successfully ingested documents into {db_path}")

if __name__ == "__main__":
    ingest_documents()
