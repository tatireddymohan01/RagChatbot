# 🤖 RAG Chatbot

AI-powered chatbot using **FastAPI** + **LangChain** with **Retrieval Augmented Generation (RAG)**. Upload documents and ask questions - get intelligent answers based on your content.

## ✨ What It Does

- 💬 **Chat with your documents** - Ask questions and get accurate answers from uploaded files
- 📄 **Multiple formats** - Supports PDF, DOCX, TXT files
- 🌐 **Web scraping** - Learn from websites and URLs
- 🧠 **Conversation memory** - Remembers context throughout the chat session
- 🎨 **Clean web UI** - Professional chat interface included
- ☁️ **Auto-deploy** - Push to GitHub → Automatically deploys to Azure
- 🔌 **REST API** - Use from any application (React, Vue, Python, Node.js, etc.)

## 🎯 Key Features

- **Intelligent Answers** - Combines your documents with OpenAI GPT-4o-mini
- **Source Citations** - Shows which documents were used to answer
- **Persistent Storage** - FAISS vector database saves processed documents
- **Session Management** - Multiple users with separate conversation histories
- **Automatic Processing** - Monitors `documents/` folder for new files
- **Production Ready** - Logging, error handling, health checks, CORS support

## 📁 Project Structure

```
RagChatbot/
├── app/                     # Backend API
│   ├── main.py              # FastAPI application entry point
│   ├── api/                 # API endpoints
│   │   ├── chat.py          # Chat endpoint - handles queries
│   │   ├── ingest.py        # Document upload endpoints
│   │   └── health.py        # Health check endpoint
│   ├── core/                # Core configuration
│   │   ├── config.py        # Environment settings
│   │   ├── llm.py           # OpenAI LLM initialization
│   │   ├── embeddings.py    # Text embeddings setup
│   │   └── vectorstore.py   # FAISS vector database manager
│   ├── services/            # Business logic
│   │   ├── rag_chain.py     # RAG pipeline implementation
│   │   ├── document_loader.py # Document processing
│   │   ├── document_monitor.py # Auto-process new files
│   │   └── web_scraper.py   # URL content extraction
│   ├── schemas/             # Data models (Pydantic)
│   │   ├── chat_schema.py   # Chat request/response models
│   │   └── ingest_schema.py # Ingestion models
│   ├── utils/
│   │   └── logger.py        # Logging configuration
│   └── data/
│       └── faiss_index/     # Vector database storage
├── ui/                      # Frontend UI
│   ├── static/
│   │   ├── style.css        # UI styles
│   │   └── script.js        # Frontend JavaScript
│   └── templates/
│       └── index.html       # Chat interface
├── documents/               # Drop documents here for auto-processing
├── logs/                    # Application logs
├── .github/workflows/       # GitHub Actions CI/CD
│   └── azure-deploy-simple.yml
├── requirements.txt         # Python dependencies
├── requirements-azure.txt   # Azure-specific requirements
├── .env                     # Environment configuration
├── .env.example            # Environment template
├── start.ps1               # Local startup script (Windows)
├── README.md               # This file
├── API_GUIDE.md            # Complete API reference
└── PROJECT_GUIDE.md        # Detailed technical explanation
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** installed
- **OpenAI API key** ([Get one here](https://platform.openai.com/api-keys))
- **Git** (for deployment)

### Installation

```bash
# 1. Clone repository
git clone <your-repo-url>
cd RagChatbot

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory:

```env
# Required
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional (defaults shown)
MODEL_NAME=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
TEMPERATURE=0.7

# Vector Store
FAISS_INDEX_PATH=app/data/faiss_index
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
RETRIEVAL_K=4

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Behavior
ALLOW_GENERAL_KNOWLEDGE=true
CORS_ORIGINS=["*"]
```

### Run Locally

```bash
# Option 1: Using uvicorn
python -m uvicorn app.main:app --reload

# Option 2: Using the startup script (Windows)
.\start.ps1

# Option 3: Direct Python
python -m app.main
```

Access the application:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## 📤 Adding Documents

### Method 1: Auto-Processing (Easiest)
1. Drop files into the `documents/` folder
2. Restart the application
3. Files are automatically processed on startup

### Method 2: Web UI - Upload Files
1. Open http://localhost:8000
2. Use the upload feature in the interface

### Method 3: Web UI - Ingest URLs ⭐
1. Open http://localhost:8000/admin
2. **Option A: Single URLs** - Enter one or more URLs (always works)
3. **Option B: Ingest from Sitemap** ⭐ *Recommended for Azure/Cloud*
   - Works on Azure, AWS Lambda, Google Cloud Run
   - Auto-discovers all URLs from sitemap.xml
   - No ChromeDriver required
   - Enter domain: `example.com` or `https://example.com`

### Method 4: API
```bash
# Upload file
curl -X POST http://localhost:8000/ingest/docs \
  -F "file=@document.pdf"

# Ingest single URL
curl -X POST http://localhost:8000/ingest/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'

# Ingest from sitemap (cloud-native)
curl -X POST http://localhost:8000/ingest/sitemap \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'
```

## 🗺️ Cloud Deployments (Azure, AWS Lambda, Google Cloud)

### Important: Use Sitemap Mode for Cloud
On Azure and other cloud platforms, **ChromeDriver is not available**. Instead of using "Full Site (auto-discover)":

1. **Use the new Sitemap feature** ⭐ (Recommended)
   - No ChromeDriver needed
   - Auto-discovers URLs from sitemap.xml
   - Works on all cloud platforms
   - In Admin console: 🗺️ **Sitemap** card

2. **Or use Single URLs mode**
   - Manually enter URLs one at a time
   - Always works, no dependencies
   - In Admin console: **Ingest from URL(s)** card

### ❌ Don't Use: Full Site (auto-discover) on Cloud
This mode requires ChromeDriver and will show:
```
(ChromeDriver unavailable)
```
This is expected - use Sitemap or Single URLs instead.

---

## ☁️ Deploy to Azure

### Quick Setup

1. **Create Azure Resources** (via Portal or CLI):
   - Resource Group: `rg-ragchatbot`
   - App Service Plan: `plan-ragchatbot` (Linux, Python 3.11)
   - Web App: `ragchatbot-app` (choose your unique name)

2. **Configure Azure Web App**:
   - Go to Configuration → Application settings
   - Add: `OPENAI_API_KEY` = your key
   - Add: `MODEL_NAME` = gpt-4o-mini
   - Add: `EMBEDDING_MODEL` = text-embedding-3-small
   - Set Startup Command: 
     ```
     gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 4 app.main:app --worker-class uvicorn.workers.UvicornWorker
     ```

3. **Setup GitHub Actions**:
   - Download publish profile from Azure Web App
   - Add to GitHub: Settings → Secrets → `AZURE_WEBAPP_PUBLISH_PROFILE`
   - Update `.github/workflows/azure-deploy-simple.yml` with your app name

4. **Deploy**:
   ```bash
   git add .
   git commit -m "Deploy to Azure"
   git push origin main
   ```

### Azure Pricing

| Tier | Cost | RAM | Storage | Use Case |
|------|------|-----|---------|----------|
| **F1 (Free)** | $0/month | 1 GB | 1 GB | Testing, demos, learning |
| **B1 (Basic)** | ~$13/month | 1.75 GB | 10 GB | Small production, always-on |
| **S1 (Standard)** | ~$70/month | 1.75 GB | 50 GB | High-traffic, auto-scaling |

**Free Tier Limitations:**
- Sleeps after 20 min inactivity
- 60 CPU minutes/day
- No custom domains

**Recommended:** Start with Free, upgrade to B1 for production (always-on, no sleep).

### OpenAI Costs

- **GPT-4o-mini**: ~$0.50-$2.00 per 1,000 chat messages
- **Pricing**: $0.15/1M input tokens, $0.60/1M output tokens
- Monitor usage: https://platform.openai.com/usage

## 📚 API Endpoints

Full documentation with examples: [API_GUIDE.md](API_GUIDE.md)

### Quick Reference

```bash
# Health Check
GET /health

# Chat
POST /chat
{
  "query": "What is machine learning?",
  "session_id": "user-123"
}

# Upload Document
POST /ingest/file
Content-Type: multipart/form-data

# Ingest URL
POST /ingest/url
{
  "url": "https://example.com/article"
}

# Add Text
POST /ingest/text
{
  "text": "Your content here...",
  "metadata": {"source": "manual"}
}
```

Interactive API testing: http://localhost:8000/docs

## 🔧 Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | **Required** |
| `MODEL_NAME` | LLM model | gpt-4o-mini |
| `EMBEDDING_MODEL` | Embedding model | text-embedding-3-small |
| `TEMPERATURE` | LLM temperature (0-1) | 0.7 |
| `CHUNK_SIZE` | Document chunk size | 1000 |
| `CHUNK_OVERLAP` | Chunk overlap | 200 |
| `RETRIEVAL_K` | Documents to retrieve | 4 |
| `ALLOW_GENERAL_KNOWLEDGE` | Use GPT for general questions | true |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |
| `DEBUG` | Debug mode | false |
| `CORS_ORIGINS` | Allowed origins | ["*"] |
| `API_ONLY` | Disable UI | false |
| `CHROME_BINARY_PATH` | Path to Chrome/Chromium (optional) | Auto-detect |

**Note:** ChromeDriver is optional. The "Full Site" mode uses it if available, but the new **Sitemap feature** doesn't need it and is recommended for cloud deployments.

## 🛠️ Development

### Project Setup for Development

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app.main:app --reload --log-level debug

# Check logs
tail -f logs/rag_chatbot_*.log
```

### Code Structure

- **app/main.py** - Application entry, CORS, startup events
- **app/api/** - FastAPI route handlers
- **app/core/** - Singleton instances (LLM, embeddings, vectorstore)
- **app/services/** - Business logic (RAG chain, document processing)
- **app/schemas/** - Pydantic models for validation
- **ui/** - Frontend HTML/CSS/JS (separate from API)

## 🔍 How It Works

See [PROJECT_GUIDE.md](PROJECT_GUIDE.md) for detailed technical explanation.

**Quick Overview:**

1. **Document Ingestion**
   - Documents split into chunks (1000 chars)
   - Converted to embeddings (vector representations)
   - Stored in FAISS vector database

2. **Query Processing**
   - User question converted to embedding
   - Similar document chunks retrieved
   - LLM generates answer using retrieved context

3. **Conversation Memory**
   - Session-based memory per user
   - Context maintained across multiple turns

## 🐛 Troubleshooting

### "No documents in vector store"
**Solution:** Upload documents first via UI or API

### "OpenAI API error"
**Solution:** 
- Verify `OPENAI_API_KEY` in `.env`
- Check credits: https://platform.openai.com/usage
- Ensure API key has access to gpt-4o-mini

### "Module not found"
**Solution:**
```bash
pip install --upgrade -r requirements.txt
```

### "Port 8000 already in use"
**Solution:** Change `PORT` in `.env` or kill existing process:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux/Mac
lsof -ti:8000 | xargs kill
```

### Azure: "Application Error"
**Solution:**
- Check Azure Log Stream for errors
- Verify environment variables are set
- Ensure startup command is correct
- Restart the Web App

### Azure: Full Site Mode Shows "(ChromeDriver unavailable)"
**Solution:** This is expected - ChromeDriver is not available on Azure Linux.
- ✅ **Use Sitemap mode instead** (recommended)
  - Go to admin console → 🗺️ **Sitemap** card
  - Enter domain: `example.com`
  - All URLs auto-discovered and ingested
- Or use Single URLs mode and enter URLs manually

### Document not processing
**Solution:**
- Check file format (PDF, DOCX, TXT)
- Verify file is in `documents/` folder
- Check logs: `logs/rag_chatbot_*.log`
- Restart application to trigger auto-processing

## 📖 Additional Documentation

- **[API_GUIDE.md](API_GUIDE.md)** - Complete API reference with integration examples (JavaScript, Python, curl)
- **[PROJECT_GUIDE.md](PROJECT_GUIDE.md)** - Deep dive into architecture, components, and how everything works

## 🔒 Security Best Practices

1. **Never commit `.env` file** - Added to `.gitignore`
2. **Use environment variables** - All secrets via env vars
3. **Restrict CORS in production** - Set specific origins in `CORS_ORIGINS`
4. **Keep dependencies updated** - Regularly update `requirements.txt`
5. **Monitor API usage** - Track OpenAI costs
6. **Use HTTPS in production** - Azure provides free SSL

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Commit: `git commit -m "Add feature"`
5. Push: `git push origin feature-name`
6. Open a Pull Request

## 📄 License

MIT License - Feel free to use for personal or commercial projects.

## 🙏 Acknowledgments

- **LangChain** - RAG framework
- **FastAPI** - Modern web framework
- **OpenAI** - GPT-4 and embeddings
- **FAISS** - Efficient vector search

## 📞 Support

- **Issues**: Open a GitHub issue
- **Documentation**: Check API_GUIDE.md and PROJECT_GUIDE.md
- **Logs**: Review `logs/` directory for errors

---

**Built with ❤️ using FastAPI, LangChain, and OpenAI** 🚀
