# Start RAG Chatbot Server
# Activates virtual environment and runs the FastAPI server

Write-Host "🤖 Starting RAG Chatbot API..." -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
& .\.venv\Scripts\Activate.ps1

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found!" -ForegroundColor Yellow
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "❌ Please edit .env and add your OPENAI_API_KEY" -ForegroundColor Red
    Write-Host "Then run this script again." -ForegroundColor Red
    exit 1
}

# Check configuration
$useHF = (Get-Content ".env" | Select-String "USE_HUGGINGFACE_LLM=true") -ne $null
$openaiKey = Get-Content ".env" | Select-String "OPENAI_API_KEY="

if ($useHF) {
    Write-Host "✅ Using HuggingFace models (local)" -ForegroundColor Green
} elseif ($openaiKey -and $openaiKey -notmatch "your-openai-api-key-here|sk-proj-") {
    Write-Host "⚠️  OpenAI API key may not be set correctly" -ForegroundColor Yellow
    Write-Host "Set USE_HUGGINGFACE_LLM=true to use local models instead" -ForegroundColor Gray
} else {
    Write-Host "✅ Configuration loaded" -ForegroundColor Green
}
Write-Host ""

# Check if port 8000 is available, otherwise use 8001
$port = 8000
$portInUse = netstat -ano | Select-String ":$port " -Quiet
if ($portInUse) {
    Write-Host "⚠️  Port $port is in use, trying port 8001..." -ForegroundColor Yellow
    $port = 8001
}

Write-Host "📡 Server will start at: http://localhost:$port" -ForegroundColor Cyan
Write-Host "📚 API Docs at: http://localhost:$port/docs" -ForegroundColor Cyan
Write-Host "🌐 Web UI at: http://localhost:$port/" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  Keep this window open - closing it will stop the server!" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run the server with auto-reload for development
python -m uvicorn app.main:app --host 127.0.0.1 --port $port --reload
