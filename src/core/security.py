from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import yaml
import os

# Load config
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "settings.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

API_KEY_NAME = "X-API-Key"
API_KEY = config["security"]["api_key"]

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
    )

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for docs and health check
        if request.url.path in ["/docs", "/openapi.json", "/health"]:
            return await call_next(request)
            
        # Basic check if needed, but FastAPI dependency is better for specific routes
        # This middleware is a catch-all if we want to enforce it globally
        # For now, we will rely on the dependency injection in routes
        response = await call_next(request)
        return response
