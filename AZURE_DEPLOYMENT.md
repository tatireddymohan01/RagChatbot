# Azure Deployment Guide for RAG Chatbot

## Prerequisites
- Azure CLI installed
- Azure subscription
- OpenAI API key

## Step 1: Install Azure CLI

### Windows
Download from: https://aka.ms/installazurecliwindows

### Linux
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### Mac
```bash
brew install azure-cli
```

## Step 2: Login to Azure

```bash
az login
```

## Step 3: Create Resources

### Set Variables
```bash
$RESOURCE_GROUP="RagChatbotRG"
$LOCATION="eastus"
$APP_SERVICE_PLAN="RagChatbotPlan"
$WEB_APP_NAME="rag-chatbot-api-unique123"  # Must be globally unique
```

### Create Resource Group
```bash
az group create --name $RESOURCE_GROUP --location $LOCATION
```

### Create App Service Plan (Linux)
```bash
az appservice plan create \
  --name $APP_SERVICE_PLAN \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku B1 \
  --is-linux
```

### Create Web App
```bash
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $APP_SERVICE_PLAN \
  --name $WEB_APP_NAME \
  --runtime "PYTHON:3.11"
```

## Step 4: Configure Application Settings

```bash
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --settings \
    OPENAI_API_KEY="your-openai-api-key" \
    MODEL_NAME="gpt-4o-mini" \
    TEMPERATURE="0.0" \
    EMBEDDING_MODEL="text-embedding-3-small" \
    CHUNK_SIZE="1000" \
    CHUNK_OVERLAP="200" \
    RETRIEVAL_K="4" \
    DEBUG="false" \
    AZURE_DEPLOYMENT="true"
```

## Step 5: Configure Startup Command

```bash
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --startup-file "uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

## Step 6: Deploy Code

### Option A: Deploy from local directory
```bash
cd d:\GitHubRepos\GenAI\RagChatbot
az webapp up --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP
```

### Option B: Deploy from GitHub
```bash
az webapp deployment source config \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --repo-url https://github.com/yourusername/RagChatbot \
  --branch main \
  --manual-integration
```

## Step 7: Enable Logging

```bash
az webapp log config \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --application-logging filesystem \
  --level information
```

## Step 8: Stream Logs

```bash
az webapp log tail \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP
```

## Step 9: Test Deployment

```bash
curl https://$WEB_APP_NAME.azurewebsites.net/health
```

## Step 10: Scale Up (Optional)

### Upgrade to Standard tier for better performance
```bash
az appservice plan update \
  --name $APP_SERVICE_PLAN \
  --resource-group $RESOURCE_GROUP \
  --sku S1
```

## Persistent Storage for FAISS Index

### Option 1: Azure Blob Storage (Recommended)

1. Create Storage Account:
```bash
az storage account create \
  --name ragchatbotstorage \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS
```

2. Get connection string:
```bash
az storage account show-connection-string \
  --name ragchatbotstorage \
  --resource-group $RESOURCE_GROUP \
  --query connectionString \
  --output tsv
```

3. Add to App Settings:
```bash
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --settings AZURE_STORAGE_CONNECTION_STRING="<connection-string>"
```

### Option 2: Azure Files

1. Create file share:
```bash
az storage share create \
  --name ragchatbotdata \
  --account-name ragchatbotstorage
```

2. Mount to web app:
```bash
az webapp config storage-account add \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --custom-id RagData \
  --storage-type AzureFiles \
  --share-name ragchatbotdata \
  --account-name ragchatbotstorage \
  --access-key "<storage-key>" \
  --mount-path /app/data
```

## CORS Configuration

```bash
az webapp cors add \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --allowed-origins "https://yourdomain.com" "https://app.yourdomain.com"
```

## SSL/HTTPS

Azure App Service provides free SSL certificates. To use custom domain:

```bash
# Add custom domain
az webapp config hostname add \
  --webapp-name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --hostname www.yourdomain.com

# Bind SSL certificate
az webapp config ssl bind \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --certificate-thumbprint <thumbprint> \
  --ssl-type SNI
```

## Monitoring with Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app ragchatbot-insights \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP

# Get instrumentation key
az monitor app-insights component show \
  --app ragchatbot-insights \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey

# Add to app settings
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY="<instrumentation-key>"
```

## Clean Up Resources

To delete all resources:
```bash
az group delete --name $RESOURCE_GROUP --yes
```

## Estimated Costs

- **Basic (B1)**: ~$13/month
- **Standard (S1)**: ~$70/month
- **Storage**: ~$0.02/GB/month
- **OpenAI API**: Pay per token usage

## Troubleshooting

### View logs
```bash
az webapp log tail --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP
```

### Restart app
```bash
az webapp restart --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP
```

### Check app settings
```bash
az webapp config appsettings list --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP
```

## Production Checklist

- [ ] Set DEBUG=false
- [ ] Configure proper CORS origins
- [ ] Enable Application Insights
- [ ] Set up persistent storage for FAISS
- [ ] Configure custom domain and SSL
- [ ] Set up automated backups
- [ ] Configure rate limiting
- [ ] Set up monitoring and alerts
- [ ] Document API endpoints
- [ ] Test all endpoints in production
