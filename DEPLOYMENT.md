# 🚀 Deployment Guide

Complete guide for deploying the RAG Chatbot to Azure using GitHub Actions.

## Table of Contents
- [GitHub Actions Deployment (Recommended)](#github-actions-deployment-recommended)
- [Local Development](#local-development)
- [Docker Deployment (Optional)](#docker-deployment-optional)

---

## 🚀 GitHub Actions Deployment (Recommended)

Automated deployment to Azure App Service using GitHub Actions.

### Prerequisites
- Azure account with active subscription
- GitHub repository
- Azure Web App created (Free F1 tier or higher)

### Step 1: Create Azure Resources Manually

1. **Login to Azure Portal:** https://portal.azure.com

2. **Create Resource Group:**
   - Search "Resource groups" → Create
   - Name: `rg-ragchatbot`
   - Region: `East US`

3. **Create App Service Plan:**
   - Search "App Service plans" → Create
   - Name: `plan-ragchatbot`
   - OS: **Linux**
   - Pricing: **F1 (Free)**

4. **Create Web App:**
   - Search "App Services" → Create → Web App
   - Name: `ragchatbot-app` (or your unique name)
   - Runtime: **Python 3.11**
   - OS: **Linux**
   - Plan: Select the plan you created

5. **Configure Environment Variables:**
   - In Web App → Settings → Environment variables
   - Add these variables:
     - `OPENAI_API_KEY` - Your OpenAI API key
     - `MODEL_NAME` - gpt-4o-mini
     - `EMBEDDING_MODEL` - text-embedding-3-small
     - `TEMPERATURE` - 0.7
     - `PORT` - 8000
     - `HOST` - 0.0.0.0
     - `DEBUG` - false
     - `ALLOW_GENERAL_KNOWLEDGE` - true
     - `SCM_DO_BUILD_DURING_DEPLOYMENT` - true

6. **Configure Startup Command:**
   - In Web App → Settings → Configuration → General settings
   - Startup Command: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
   - Click Save

### Step 2: Setup GitHub Actions

1. **Get Publish Profile from Azure:**
   - In your Web App overview, click **"Get publish profile"**
   - Save the downloaded `.PublishSettings` file
   - Open it and copy all the XML content

2. **Add Secret to GitHub:**
   - Go to your GitHub repository
   - Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `AZURE_WEBAPP_PUBLISH_PROFILE`
   - Value: Paste the XML content
   - Click "Add secret"

3. **Update Workflow (if needed):**
   - Edit `.github/workflows/azure-deploy-simple.yml`
   - Change `AZURE_WEBAPP_NAME` to your Web App name:
     ```yaml
     env:
       AZURE_WEBAPP_NAME: your-webapp-name  # Change this
     ```

### Step 3: Deploy

**Option 1 - Push to main branch:**
```bash
git add .
git commit -m "Deploy to Azure"
git push origin main
```

**Option 2 - Manual trigger:**
1. Go to GitHub → Actions
2. Click "Deploy to Azure Web App"
3. Click "Run workflow" → "Run workflow"

### Step 4: Monitor Deployment

- Watch progress in GitHub Actions tab
- Check logs in Azure Portal → Log stream
- Access your app at: `https://your-app.azurewebsites.net`

### Testing Endpoints

- **Main App:** `https://your-app.azurewebsites.net/`
- **Health Check:** `https://your-app.azurewebsites.net/health`
- **API Docs:** `https://your-app.azurewebsites.net/docs`

---

## 🐳 Docker Deployment (Optional)

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

---

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
