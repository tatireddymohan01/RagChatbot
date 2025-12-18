# 🚀 Deployment Guide

Complete guide for deploying the RAG Chatbot to various platforms.

## Table of Contents
- [Docker Deployment](#docker-deployment)
- [Azure App Service](#azure-app-service)
- [Local Development](#local-development)

---

## 🐳 Docker Deployment

### Quick Start with Docker Compose

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Manual Docker Build

```bash
# Build image
docker build -t ragchatbot:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY="your-key-here" \
  --name ragchatbot \
  ragchatbot:latest
```

### Docker Configuration

The `docker-compose.yml` includes:
- FastAPI backend on port 8000
- Health checks
- Volume mounts for data persistence
- Environment variable configuration

---

## ☁️ Azure App Service

### Prerequisites
- Azure account with active subscription
- Azure CLI installed
- GitHub repository
- Docker installed for testing

### 1. Create Azure Resources

```bash
# Login to Azure
az login

# Create resource group
az group create --name rg-ragchatbot --location eastus

# Create Azure Container Registry
az acr create \
  --resource-group rg-ragchatbot \
  --name ragchatbotacr \
  --sku Basic \
  --admin-enabled true

# Create App Service Plan (Linux)
az appservice plan create \
  --name plan-ragchatbot \
  --resource-group rg-ragchatbot \
  --is-linux \
  --sku B1

# Create Web App
az webapp create \
  --resource-group rg-ragchatbot \
  --plan plan-ragchatbot \
  --name ragchatbot-app \
  --deployment-container-image-name ragchatbotacr.azurecr.io/ragchatbot:latest
```

### 2. Configure Environment Variables

```bash
az webapp config appsettings set \
  --name ragchatbot-app \
  --resource-group rg-ragchatbot \
  --settings \
    OPENAI_API_KEY="your-openai-api-key" \
    MODEL_NAME="gpt-4o-mini" \
    WEBSITES_PORT="8000" \
    WEBSITES_ENABLE_APP_SERVICE_STORAGE="true"
```

### 3. GitHub Actions Setup

Add these secrets to your GitHub repository:
- `AZURE_CREDENTIALS` - Azure service principal
- `AZURE_REGISTRY_LOGIN_SERVER` - ACR login server
- `AZURE_REGISTRY_USERNAME` - ACR username
- `AZURE_REGISTRY_PASSWORD` - ACR password
- `OPENAI_API_KEY` - OpenAI API key

The included `.github/workflows/azure-deploy.yml` handles CI/CD automatically.

### 4. Deploy

```bash
# Push to main branch to trigger deployment
git push origin main
```

### Monitoring

```bash
# View logs
az webapp log tail --name ragchatbot-app --resource-group rg-ragchatbot

# Check status
az webapp show --name ragchatbot-app --resource-group rg-ragchatbot --query state
```

---

## 💻 Local Development

### Setup

```bash
# Clone repository
git clone <your-repo-url>
cd RagChatbot

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Run

```bash
# Windows:
.\start.ps1

# Linux/Mac:
uvicorn app.main:app --reload
```

### Access
- Web UI: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

## 🎯 Configuration Options

### OpenAI vs HuggingFace

**OpenAI (Recommended for Azure):**
```env
USE_HUGGINGFACE_EMBEDDINGS=false
USE_HUGGINGFACE_LLM=false
OPENAI_API_KEY=your-key-here
```

**HuggingFace (Local, requires 16GB+ RAM):**
```env
USE_HUGGINGFACE_EMBEDDINGS=true
USE_HUGGINGFACE_LLM=true
HUGGINGFACE_CACHE_DIR=D:/HuggingFace/cache
```

### API-Only Mode

To deploy without the built-in UI (use with external frontend):
```env
API_ONLY=true
```

### CORS Configuration

For production with external frontend:
```env
CORS_ORIGINS=["https://your-frontend-domain.com"]
```

---

## 🔧 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Windows:
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

**Docker build fails:**
```bash
# Clear Docker cache
docker system prune -a
```

**HuggingFace out of memory:**
- Switch to OpenAI API
- Or increase VM size in Azure (requires 16GB+ RAM)

---

## 📊 Performance Tips

1. **Use OpenAI API** for Azure deployments (more cost-effective than large VMs)
2. **Enable caching** in production
3. **Use Azure Container Registry** for faster deployments
4. **Configure health checks** for automatic restarts
5. **Monitor logs** for performance issues

---

## 🔒 Security Best Practices

1. Never commit `.env` files or API keys to Git
2. Use Azure Key Vault for production secrets
3. Enable HTTPS only in production
4. Configure proper CORS origins
5. Regularly update dependencies

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [Azure App Service Documentation](https://docs.microsoft.com/azure/app-service/)
- [Docker Documentation](https://docs.docker.com/)
