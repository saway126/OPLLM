from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import requests
import yaml
import os
import logging
from src.core.security import get_api_key

# Load Config
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "settings.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

# Setup Logging
logging.basicConfig(
    filename=config["logging"]["file_path"],
    level=getattr(logging, config["logging"]["level"]),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title=config["app"]["name"], version="1.0.0")

# Models
class ChatRequest(BaseModel):
    model: str = config["ollama"]["default_model"]
    messages: List[Dict[str, str]]
    stream: bool = False

class EmbeddingRequest(BaseModel):
    model: str = config["ollama"]["embedding_model"]
    prompt: str

class RAGQueryRequest(BaseModel):
    query: str
    model: str = config["ollama"]["default_model"]
    top_k: int = 3

# Ollama Client Helper
OLLAMA_BASE = os.environ.get("OLLAMA_BASE_URL", config["ollama"]["base_url"])

def call_ollama(endpoint: str, payload: Dict[str, Any], stream: bool = False):
    try:
        url = f"{OLLAMA_BASE}/api/{endpoint}"
        response = requests.post(url, json=payload, stream=stream)
        response.raise_for_status()
        if stream:
            return response.iter_lines()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Ollama connection error: {e}")
        raise HTTPException(status_code=502, detail=f"LLM Service Unavailable: {str(e)}")

# Routes
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Air-gapped LLM Server"}

@app.post("/api/chat", dependencies=[Depends(get_api_key)])
async def chat(request: ChatRequest):
    logger.info(f"Chat request for model: {request.model}")
    payload = {
        "model": request.model,
        "messages": request.messages,
        "stream": request.stream
    }
    # Note: Streaming implementation requires StreamingResponse, simplified here for JSON
    if request.stream:
        raise HTTPException(status_code=501, detail="Streaming not implemented in this proxy yet")
    
    return call_ollama("chat", payload)

@app.post("/api/embedding", dependencies=[Depends(get_api_key)])
async def embedding(request: EmbeddingRequest):
    logger.info(f"Embedding request")
    payload = {
        "model": request.model,
        "prompt": request.prompt
    }
    return call_ollama("embeddings", payload)

# Placeholder for RAG - will be connected to src.rag.retriever
from src.rag.retriever import query_rag

@app.post("/api/rag/query", dependencies=[Depends(get_api_key)])
async def rag_query(request: RAGQueryRequest):
    logger.info(f"RAG query: {request.query}")
    try:
        response = query_rag(request.query, request.model, request.top_k)
        return response
    except Exception as e:
        logger.error(f"RAG error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config["app"]["host"], port=config["app"]["port"])
