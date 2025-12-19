# GitHub Secrets Setup for Azure Deployment

## Required Secret

You need to add this secret to your GitHub repository:

### AZURE_WEBAPP_PUBLISH_PROFILE

**Steps to get publish profile from Azure Portal:**

1. Go to **https://portal.azure.com**

2. Navigate to your Web App:
   - Search for **"App Services"** in the top search bar
   - Click on your Web App: **ragchatbot-app**

3. Download the publish profile:
   - In the Web App overview page, click **"Get publish profile"** button at the top
   - A `.PublishSettings` file will be downloaded

4. Open the downloaded file and copy all the XML content

5. Add to GitHub:
   - Go to your GitHub repository
   - Click **Settings** → **Secrets and variables** → **Actions**
   - Click **New repository secret**
   - Name: `AZURE_WEBAPP_PUBLISH_PROFILE`
   - Value: Paste the entire XML content from the publish profile file
   - Click **Add secret**

---

## Environment Variables (Set in Azure Portal)

These should already be configured in your Web App via Azure Portal. If not, configure them manually:

Go to: **Azure Portal** → **Your Web App** → **Settings** → **Environment variables**

Add these variables:
- `OPENAI_API_KEY` - Your OpenAI API key
- `MODEL_NAME` - gpt-4o-mini
- `EMBEDDING_MODEL` - text-embedding-3-small
- `TEMPERATURE` - 0.7
- `PORT` - 8000
- `HOST` - 0.0.0.0
- `DEBUG` - false
- `ALLOW_GENERAL_KNOWLEDGE` - true
- `SCM_DO_BUILD_DURING_DEPLOYMENT` - true

---

## Quick Setup Commands

Run these commands to get your Azure credentials:

```powershell
# Login to Azure
az login

# Get subscription ID
$subscriptionId = az account show --query id --output tsv
Write-Host "Subscription ID: $subscriptionId"

# Create service principal and get credentials
az ad sp create-for-rbac --name "ragchatbot-github" --role contributor --scopes /subscriptions/$subscriptionId/resourceGroups/rg-ragchatbot --sdk-auth
```

Copy the JSON output and add it to GitHub secrets as `AZURE_CREDENTIALS`.

---

## Verify Setup

After adding secrets:

1. Go to GitHub repository → **Actions**
2. Click **Deploy to Azure Web App** workflow
3. Click **Run workflow** → **Run workflow**
4. Watch the deployment progress

---

## Deployment Flow

Once configured:

1. **Push to main branch** → Automatic deployment
2. **Manual trigger** → Go to Actions → Run workflow
3. **Monitor logs** → Click on workflow run to see progress

---

## Update Web App Name

If your Web App name is different, update in `.github/workflows/azure-deploy-simple.yml`:

```yaml
env:
  AZURE_WEBAPP_NAME: your-webapp-name  # Change this
```

---

## Troubleshooting

**Service principal creation fails:**
```powershell
# Use your actual subscription ID
az ad sp create-for-rbac --name "ragchatbot-github-2" --role contributor --scopes /subscriptions/<subscription-id> --sdk-auth
```

**Deployment fails:**
- Check GitHub Actions logs
- Verify secrets are correctly set
- Ensure Web App exists in Azure Portal

---

## Next Steps

1. Add secrets to GitHub (AZURE_CREDENTIALS and OPENAI_API_KEY)
2. Push code to main branch or manually trigger workflow
3. Your app will automatically deploy! 🎉
