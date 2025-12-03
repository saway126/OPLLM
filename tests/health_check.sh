#!/bin/bash
# health_check.sh
# Verifies the system status and API functionality.

API_URL="http://localhost:8000"
API_KEY="change-me-to-a-secure-random-key" # Must match config/settings.yaml

echo "=== Starting System Health Check ==="

# 1. Check Ollama Service
echo "[1] Checking Ollama Service..."
if systemctl is-active --quiet ollama; then
    echo "PASS: Ollama service is running."
else
    echo "FAIL: Ollama service is NOT running."
fi

# 2. Check API Server
echo "[2] Checking API Server..."
HTTP_STATUS=$(curl -o /dev/null -s -w "%{http_code}\n" "$API_URL/health")
if [ "$HTTP_STATUS" == "200" ]; then
    echo "PASS: API Server is reachable ($API_URL/health)."
else
    echo "FAIL: API Server is not responding (Status: $HTTP_STATUS)."
fi

# 3. Test Chat API
echo "[3] Testing Chat API..."
RESPONSE=$(curl -s -X POST "$API_URL/api/chat" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{
        "model": "llama3",
        "messages": [{"role": "user", "content": "Hello, are you working?"}]
    }')

if [[ "$RESPONSE" == *"message"* ]] || [[ "$RESPONSE" == *"response"* ]]; then
    echo "PASS: Chat API returned a valid response."
else
    echo "WARNING: Chat API response unexpected (Check if model 'llama3' is loaded)."
    echo "Response: $RESPONSE"
fi

echo "=== Health Check Complete ==="
