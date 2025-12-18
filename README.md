# 🤖 RAG Chatbot - Full Stack AI Application

Production-grade chatbot using **FastAPI** + **LangChain** with **Retrieval Augmented Generation (RAG)**. Supports both monolithic and separated frontend/backend deployment.

## 🌟 Features

### Core Features
- ✅ **REST API** with FastAPI - Clean, well-documented API
- ✅ **RAG Architecture** using LangChain - Context-aware responses
- ✅ **Multi-format Document Support** (PDF, DOCX, TXT)
- ✅ **Web Scraping** for URL content ingestion
- ✅ **FAISS Vector Store** with persistence
- ✅ **Conversational Memory** for multi-turn dialogues
- ✅ **OpenAI GPT-4** integration with general knowledge fallback
- ✅ **Production-ready** with logging, error handling, CORS

### UI & UX
- ✅ **Professional Web UI** - Modern, demo-ready interface
- ✅ **Standalone Frontend** - Deploy independently from API
- ✅ **Toast notifications** and visual feedback
- ✅ **Responsive design** - Mobile, tablet, and desktop optimized
- ✅ **Live statistics** - Document and message counters

### Deployment & Integration
- ✅ **Separated Architecture** - API-only mode for external frontends
- ✅ **Docker containerization** - Multi-stage builds
- ✅ **CI/CD with GitHub Actions** - Automated testing and deployment
- ✅ **Azure App Service** deployment ready
- ✅ **Flexible CORS** - Configure for any frontend domain
- ✅ **Integration examples** - React, Vue, Angular, Python, Node.js

## 📁 Project Structure

```
RagChatbot/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── static/                 # Static files (CSS, JS)
│   │   ├── style.css          # UI styles
│   │   └── script.js          # Frontend JavaScript
│   ├── templates/              # HTML templates
│   │   └── index.html         # Chat UI
│   ├── api/                    # API endpoints
│   │   ├── chat.py            # Chat endpoint
│   │   ├── ingest.py          # Document/URL ingestion endpoints
│   │   └── health.py          # Health check endpoint
│   ├── core/                   # Core modules
│   │   ├── config.py          # Configuration management
│   │   ├── llm.py             # LLM initialization
│   │   ├── embeddings.py      # Embeddings management
│   │   └── vectorstore.py     # FAISS vector store manager
│   ├── services/               # Business logic services
│   │   ├── rag_chain.py       # RAG chain implementation
│   │   ├── document_loader.py # Document loading & chunking
│   │   └── web_scraper.py     # Web scraping service
│   ├── schemas/                # Pydantic models
│   │   ├── chat_schema.py     # Chat request/response models
│   │   └── ingest_schema.py   # Ingestion models
│   ├── utils/                  # Utilities
│   │   └── logger.py          # Logging configuration
│   └── data/                   # Data storage
│       └── faiss_index/       # FAISS vector store
├── .github/workflows/          # CI/CD pipelines
│   └── azure-deploy.yml       # Azure deployment workflow
├── Dockerfile                  # Docker container configuration
├── docker-compose.yml          # Docker Compose orchestration
├── .dockerignore              # Docker build exclusions
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── AZURE_DEPLOYMENT.md        # Azure deployment guide
└── DOCKER_DEPLOYMENT.md       # Docker & deployment guide
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- OpenAI API key
- pip or conda

### 1. Clone the Repository

```bash
cd d:\GitHubRepos\GenAI\RagChatbot
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example environment file
copy .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-api-key-here
```

**Required Environment Variables:**
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `MODEL_NAME`: OpenAI model to use (default: gpt-4o-mini)
- `EMBEDDING_MODEL`: Embedding model (default: text-embedding-3-small)

### 5. Run the Application

```bash
# Run with uvicorn
uvicorn app.main:app --reload

# Or run directly
python -m app.main
```

The API will be available at: `http://localhost:8000`

### 6. Access the Application

- **Web UI**: http://localhost:8000/ (Interactive chat interface)
- **Swagger UI**: http://localhost:8000/docs (API documentation)
- **ReDoc**: http://localhost:8000/redoc (Alternative API docs)

## 🏗️ Deployment Modes

This application supports two deployment architectures:

### 1. **Monolithic (Default)**
Full-stack deployment with API and UI served from the same server.

```env
API_ONLY=false  # or omit this variable
```

**Use when:**
- Simple deployments
- Quick demos
- Small-scale applications

### 2. **Separated (Microservices)**
API and Frontend deployed independently for better scalability.

**Backend (API-only):**
```env
API_ONLY=true
CORS_ORIGINS=["https://your-frontend.com"]
```

**Frontend (Standalone):**
```javascript
// frontend/config.js
API_BASE_URL: 'https://your-api-domain.com'
```

**Use when:**
- Integrating with existing applications
- Multiple frontend applications
- Better scalability and independent updates
- Mobile app backends

**Learn more:**
- [📖 API Documentation](./API_DOCUMENTATION.md) - Complete API reference
- [🔧 Separated Architecture Guide](./SEPARATED_ARCHITECTURE.md) - Deployment options
- [💡 Integration Examples](./INTEGRATION_EXAMPLES.md) - React, Vue, Python, etc.

## 📚 API Endpoints

### Health Check

```bash
GET /health
```

Returns API status and configuration info.

### Chat

```bash
POST /chat
```

**Request Body:**
```json
{
  "query": "What is machine learning?",
  "session_id": "user-123",
  "chat_history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"}
  ]
}
```

**Response:**
```json
{
  "answer": "Machine learning is...",
  "sources": [
    {
      "content": "Machine learning is a method...",
      "source": "ml_intro.pdf",
      "page": 1
    }
  ],
  "session_id": "user-123"
}
```

### Ingest Documents

```bash
POST /ingest/docs
```

Upload PDF, DOCX, or TXT files.

**Form Data:**
- `files`: Multiple file uploads (multipart/form-data)

**Response:**
```json
{
  "status": "success",
  "message": "Successfully ingested 3 document(s)",
  "documents_processed": 3,
  "chunks_created": 45,
  "sources": ["doc1.pdf", "doc2.docx", "doc3.txt"]
}
```

### Ingest URL

```bash
POST /ingest/url
```

**Request Body:**
```json
{
  "url": "https://en.wikipedia.org/wiki/Artificial_intelligence"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Successfully ingested content from URL",
  "documents_processed": 1,
  "chunks_created": 23,
  "sources": ["https://en.wikipedia.org/wiki/Artificial_intelligence"]
}
```

## 🧪 Testing with cURL

### Health Check

```bash
curl http://localhost:8000/health
```

### Ingest a Document

```bash
curl -X POST "http://localhost:8000/ingest/docs" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@document.pdf"
```

### Ingest from URL

```bash
curl -X POST "http://localhost:8000/ingest/url" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"https://en.wikipedia.org/wiki/Machine_learning\"}"
```

### Chat Query

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"What is machine learning?\",\"session_id\":\"user-123\"}"
```

### Chat with History

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"Tell me more about neural networks\",
    \"session_id\": \"user-123\",
    \"chat_history\": [
      {\"role\": \"user\", \"content\": \"What is deep learning?\"},
      {\"role\": \"assistant\", \"content\": \"Deep learning is a subset of machine learning...\"}
    ]
  }"
```

## 🧪 Testing with PowerShell

### Health Check

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
```

### Ingest Document

```powershell
$filePath = "C:\path\to\document.pdf"
$url = "http://localhost:8000/ingest/docs"

$form = @{
    files = Get-Item -Path $filePath
}

Invoke-RestMethod -Uri $url -Method Post -Form $form
```

### Ingest URL

```powershell
$body = @{
    url = "https://en.wikipedia.org/wiki/Machine_learning"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/ingest/url" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"
```

### Chat

```powershell
$body = @{
    query = "What is machine learning?"
    session_id = "user-123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/chat" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"
```

## ⚙️ Configuration

All configuration is managed through environment variables in `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | **Required** |
| `MODEL_NAME` | OpenAI model name | gpt-4o-mini |
| `TEMPERATURE` | LLM temperature | 0.0 |
| `EMBEDDING_MODEL` | Embedding model | text-embedding-3-small |
| `USE_HUGGINGFACE_EMBEDDINGS` | Use HuggingFace instead of OpenAI | false |
| `CHUNK_SIZE` | Text chunk size | 1000 |
| `CHUNK_OVERLAP` | Text chunk overlap | 200 |
| `RETRIEVAL_K` | Number of docs to retrieve | 4 |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |
| `DEBUG` | Debug mode | false |

## 🏭 Production Deployment

### Azure Deployment

The application is Azure-ready with:

1. **Environment variable support** for all configuration
2. **CORS middleware** for cross-origin requests
3. **Health check endpoint** for load balancers
4. **Logging** to files and console
5. **Graceful startup/shutdown**

#### Azure App Service Deployment

```bash
# Install Azure CLI
# https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

# Login
az login

# Create resource group
az group create --name RagChatbotRG --location eastus

# Create App Service plan
az appservice plan create --name RagChatbotPlan --resource-group RagChatbotRG --sku B1 --is-linux

# Create web app
az webapp create --resource-group RagChatbotRG --plan RagChatbotPlan --name rag-chatbot-api --runtime "PYTHON:3.11"

# Configure environment variables
az webapp config appsettings set --resource-group RagChatbotRG --name rag-chatbot-api --settings OPENAI_API_KEY="your-key"

# Deploy code
az webapp up --name rag-chatbot-api --resource-group RagChatbotRG
```

### Docker Deployment (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t rag-chatbot .
docker run -p 8000:8000 --env-file .env rag-chatbot
```

## 🔒 Security Best Practices

1. **Never commit `.env` file** - Keep API keys secret
2. **Use environment variables** for all sensitive data
3. **Enable CORS** only for trusted origins in production
4. **Implement rate limiting** for production APIs
5. **Use HTTPS** in production
6. **Validate all inputs** (already implemented with Pydantic)

## 🐛 Troubleshooting

### Issue: FAISS index not persisting

**Solution:** Ensure the `app/data/faiss_index` directory has write permissions.

### Issue: "No documents in vector store"

**Solution:** Ingest some documents first using `/ingest/docs` or `/ingest/url` endpoints.

### Issue: OpenAI API errors

**Solution:** 
- Check your API key in `.env`
- Verify you have API credits
- Check OpenAI service status

### Issue: Module import errors

**Solution:**
```bash
pip install --upgrade -r requirements.txt
```

## � Docker & Deployment

### Run with Docker

```bash
# Build image
docker build -t ragchatbot:latest .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Access at: http://localhost:8000

### Deploy to Azure App Service

Complete deployment guide: [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md)

**Quick Azure Setup:**
```bash
# Create resources
az group create --name rg-ragchatbot --location eastus
az acr create --resource-group rg-ragchatbot --name ragchatbotacr --sku Basic
az appservice plan create --name plan-ragchatbot --resource-group rg-ragchatbot --is-linux --sku B1
az webapp create --resource-group rg-ragchatbot --plan plan-ragchatbot --name ragchatbot-app \
  --deployment-container-image-name ragchatbotacr.azurecr.io/ragchatbot:latest

# Configure
az webapp config appsettings set --name ragchatbot-app --resource-group rg-ragchatbot \
  --settings OPENAI_API_KEY="sk-xxx" WEBSITES_PORT="8000"
```

### CI/CD Pipeline

Automated deployment with GitHub Actions:
- **Push to `main`**: Deploy to production
- **Push to `develop`**: Deploy to staging  
- **Pull requests**: Run tests

Setup: Add secrets in GitHub → Settings → Secrets:
- `AZURE_CREDENTIALS`
- `AZURE_REGISTRY_LOGIN_SERVER`
- `AZURE_REGISTRY_USERNAME`
- `AZURE_REGISTRY_PASSWORD`
- `OPENAI_API_KEY`

See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for more deployment options (AWS, GCP, Kubernetes).

## �📖 How It Works

### RAG Pipeline

1. **Document Ingestion**
   - Load documents (PDF/DOCX/TXT/URL)
   - Split into chunks (1000 chars with 200 overlap)
   - Generate embeddings
   - Store in FAISS vector database

2. **Query Processing**
   - User sends a question
   - System retrieves top-k relevant chunks
   - LLM generates answer using only retrieved context
   - Returns answer with source citations

3. **Conversational Memory**
   - Maintains chat history per session
   - Enables multi-turn conversations
   - Context-aware responses

### System Prompt

The system enforces strict grounding:
- Answer ONLY from retrieved context
- Say "I don't know" if answer not in context
- No external knowledge allowed
- Cite sources when possible

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [API Documentation](./API_DOCUMENTATION.md) | Complete REST API reference with examples |
| [Separated Architecture Guide](./SEPARATED_ARCHITECTURE.md) | Deploy frontend and backend independently |
| [Integration Examples](./INTEGRATION_EXAMPLES.md) | Code examples for React, Vue, Python, Node.js, etc. |
| [Azure Deployment](./AZURE_DEPLOYMENT.md) | Step-by-step Azure deployment guide |
| [Docker Deployment](./DOCKER_DEPLOYMENT.md) | Docker, AWS, GCP, Kubernetes deployment |
| [General Knowledge Guide](./GENERAL_KNOWLEDGE_GUIDE.md) | Configure AI fallback behavior |
| [Frontend README](./frontend/README.md) | Standalone frontend deployment |

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **LangChain** for the RAG framework
- **FastAPI** for the web framework
- **OpenAI** for LLM and embeddings
- **FAISS** for vector storage

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the [API Guide](./API_GUIDE.md) for integration details
- See [Deployment Guide](./DEPLOYMENT.md) for setup instructions
- Check server logs in `logs/` directory

## 🚀 Use Cases

- **Customer Support** - Answer questions from documentation
- **Knowledge Management** - Search and query internal documents
- **Research Assistant** - Extract insights from research papers
- **Educational Tools** - Interactive learning from textbooks
- **Content Q&A** - Website chatbots for content-based queries

---

**Built with ❤️ using FastAPI, LangChain, and OpenAI**
