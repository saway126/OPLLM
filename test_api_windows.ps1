# test_api_windows.ps1
# PowerShell script to test the API endpoints

$BaseUrl = "http://localhost:8000"
$ApiKey = "change-me-to-a-secure-random-key"

Write-Host "=== Starting API Test on Windows ===" -ForegroundColor Cyan

# 1. Health Check
Write-Host "`n[1] Checking Server Health..."
try {
    $health = Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get
    Write-Host "PASS: Server is running. Status: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "FAIL: Server is not reachable. Is run_server_windows.bat running?" -ForegroundColor Red
    exit
}

# 2. Chat API Test
Write-Host "`n[2] Testing Chat API..."
$chatPayload = @{
    model = "llama3"
    messages = @(
        @{ role = "user"; content = "Hello, this is a test." }
    )
} | ConvertTo-Json -Depth 3

try {
    Invoke-RestMethod -Uri "$BaseUrl/api/chat" -Method Post -Body $chatPayload -ContentType "application/json" -Headers @{ "X-API-Key" = $ApiKey } | Out-Null
    Write-Host "PASS: Chat API responded." -ForegroundColor Green
} catch {
    Write-Host "WARNING: Chat API failed. This is expected if Ollama is not installed or 'llama3' model is missing." -ForegroundColor Yellow
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Gray
}

# 3. RAG Query Test
Write-Host "`n[3] Testing RAG Query..."
$ragPayload = @{
    query = "test query"
    model = "llama3"
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "$BaseUrl/api/rag/query" -Method Post -Body $ragPayload -ContentType "application/json" -Headers @{ "X-API-Key" = $ApiKey } | Out-Null
    Write-Host "PASS: RAG API responded." -ForegroundColor Green
} catch {
    Write-Host "WARNING: RAG API failed. (Expected if Ollama/ChromaDB is not ready)" -ForegroundColor Yellow
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Gray
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
