FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copy offline wheels if available
COPY offline_pip /tmp/offline_pip
COPY requirements.txt .

ARG USE_OFFLINE_PIP=true

RUN if [ "$USE_OFFLINE_PIP" = "true" ]; then \
        pip install --no-index --find-links /tmp/offline_pip --requirement requirements.txt && \
        pip install --no-index --find-links /tmp/offline_pip langchain==0.2.16 langchain-community==0.2.16 ; \
    else \
        pip install --upgrade pip && \
        pip install --requirement requirements.txt && \
        pip install langchain==0.2.16 langchain-community==0.2.16 ; \
    fi

COPY src ./src
COPY config ./config

RUN mkdir -p /app/logs

ENV PYTHONPATH=/app \
    OLLAMA_BASE_URL=http://ollama-offline:11434

EXPOSE 8000

CMD ["python", "-m", "src.main"]

