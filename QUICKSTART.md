# 🚀 Quick Start Guide

## ⚡ Fast Setup (5 minutes)

### 1. Install Dependencies (Wait for completion)
The packages are currently installing in the background. This takes 5-10 minutes.

### 2. Configure Your API Key
Edit the `.env` file and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Start the Server
```powershell
.\start.ps1
```

Or manually:
```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

### 4. Access the Application

- **Web UI**: http://localhost:8000/ui
- **API Docs**: http://localhost:8000/docs  
- **Health Check**: http://localhost:8000/health

## 🎯 First Steps

### Step 1: Ingest Documents

Option A - Upload a file:
```powershell
$form = @{ files = Get-Item -Path "path\to\document.pdf" }
Invoke-RestMethod -Uri "http://localhost:8000/ingest/docs" -Method Post -Form $form
```

Option B - Scrape a website:
```powershell
$body = @{ url = "https://en.wikipedia.org/wiki/Machine_learning" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/ingest/url" -Method Post -Body $body -ContentType "application/json"
```

### Step 2: Ask Questions

```powershell
$body = @{ query = "What is machine learning?" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -Body $body -ContentType "application/json"
```

Or use the Web UI at http://localhost:8000/ui

## ✅ Ready!

Your RAG chatbot is ready to use. The system will:
1. Retrieve relevant document chunks
2. Generate answers grounded in your documents
3. Provide source citations

## ❓ Troubleshooting

**Packages still installing?**
- Wait for the pip install to complete (check terminal)
- Or run: `pip install -r requirements.txt`

**OpenAI API errors?**
- Check your API key in `.env`
- Verify you have credits: https://platform.openai.com/usage

**Port already in use?**
- Change PORT in `.env` file
- Or use: `python -m uvicorn app.main:app --port 8001`
