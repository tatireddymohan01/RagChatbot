# Azure CLI Deployment Script - Forces Oryx Build
Write-Host "=== Azure Deployment with Oryx Build ===" -ForegroundColor Cyan

$resourceGroup = "rg-ragchatbot"
$webAppName = "ragchatbot-app"
$location = "centralindia"

# Check Azure login
Write-Host "`nChecking Azure login..." -ForegroundColor Yellow
$account = az account show 2>$null
if (-not $account) {
    Write-Host "Please login to Azure..." -ForegroundColor Red
    az login
}

Write-Host "Logged in successfully" -ForegroundColor Green

# Stop the web app to clear any locks
Write-Host "`nStopping web app to clear deployment locks..." -ForegroundColor Yellow
az webapp stop --name $webAppName --resource-group $resourceGroup

Start-Sleep -Seconds 5

# Start the web app
Write-Host "Starting web app..." -ForegroundColor Yellow
az webapp start --name $webAppName --resource-group $resourceGroup

# Deploy using zip with SCM build
Write-Host "`nCreating deployment package..." -ForegroundColor Yellow
if (Test-Path "deploy.zip") {
    Remove-Item "deploy.zip" -Force
}

# Create ZIP excluding unnecessary files
Compress-Archive -Path `
    "app", `
    "requirements.txt", `
    "DEPLOYMENT.md", `
    "README.md", `
    ".deployment" `
    -DestinationPath "deploy.zip" -Force

Write-Host "Deployment package created: $(Get-Item deploy.zip | Select-Object -ExpandProperty Length) bytes" -ForegroundColor Green

# Deploy with Azure CLI - this respects SCM_DO_BUILD_DURING_DEPLOYMENT
Write-Host "`nDeploying to Azure..." -ForegroundColor Yellow
az webapp deployment source config-zip `
    --resource-group $resourceGroup `
    --name $webAppName `
    --src deploy.zip

Write-Host "`n=== Deployment Complete ===" -ForegroundColor Green
Write-Host "App URL: https://$webAppName.azurewebsites.net" -ForegroundColor Cyan
Write-Host "`nChecking logs in 10 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Show recent logs
Write-Host "`nRecent logs:" -ForegroundColor Yellow
az webapp log tail --name $webAppName --resource-group $resourceGroup --only-show-errors
