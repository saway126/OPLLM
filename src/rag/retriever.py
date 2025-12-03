import os
import yaml
import logging
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA

# Load Config
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "settings.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

logger = logging.getLogger(__name__)

def query_rag(query: str, model_name: str, top_k: int = 3):
    db_path = config["rag"]["chroma_db_path"]
    embedding_model_name = config["ollama"]["embedding_model"]
    base_url = config["ollama"]["base_url"]
    
    # Initialize Embeddings
    embeddings = OllamaEmbeddings(
        base_url=base_url,
        model=embedding_model_name
    )
    
    # Load Vector DB
    vector_db = Chroma(persist_directory=db_path, embedding_function=embeddings)
    
    # Initialize LLM
    llm = Ollama(
        base_url=base_url,
        model=model_name
    )
    
    # Create Retrieval Chain
    retriever = vector_db.as_retriever(search_kwargs={"k": top_k})
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    
    # Execute Query
    result = qa_chain.invoke({"query": query})
    
    # Format Response
    response = {
        "result": result["result"],
        "source_documents": [doc.page_content for doc in result["source_documents"]]
    }
    
    return response
