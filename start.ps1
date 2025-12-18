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

# Check if OPENAI_API_KEY is set
$envContent = Get-Content ".env" | Select-String "OPENAI_API_KEY="
if ($envContent -match "your-openai-api-key-here") {
    Write-Host "❌ Please set your OPENAI_API_KEY in .env file" -ForegroundColor Red
    Write-Host "Edit .env and replace 'your-openai-api-key-here' with your actual API key" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Configuration loaded" -ForegroundColor Green
Write-Host ""
Write-Host "📡 Server will start at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🌐 Web UI at: http://localhost:8000/ui" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run the server
python -m uvicorn app.main:app --reload
