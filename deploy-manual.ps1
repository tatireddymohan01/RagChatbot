# Manual deployment script to avoid GitHub Actions 409 conflicts
Write-Host "=== Manual Azure Deployment ===" -ForegroundColor Cyan

# Check if logged in to Azure
Write-Host "`nChecking Azure login..." -ForegroundColor Yellow
$account = az account show 2>$null
if (-not $account) {
    Write-Host "Not logged in. Please login to Azure..." -ForegroundColor Red
    az login
}

$subscription = az account show --query name -o tsv
Write-Host "Using subscription: $subscription" -ForegroundColor Green

# Configuration
$resourceGroup = "rg-ragchatbot"
$webAppName = "ragchatbot-app"

# Stop any in-progress deployments
Write-Host "`nStopping any in-progress deployments..." -ForegroundColor Yellow
az webapp deployment source delete --name $webAppName --resource-group $resourceGroup 2>$null

# Create deployment package
Write-Host "`nCreating deployment package..." -ForegroundColor Yellow
if (Test-Path "deploy.zip") {
    Remove-Item "deploy.zip" -Force
}

# Create ZIP excluding unnecessary files
$exclude = @(".git", ".github", "venv", ".venv", "__pycache__", "logs", ".env", "*.pyc", ".gitignore")
$files = Get-ChildItem -Path . -Recurse -File | Where-Object {
    $file = $_
    $shouldExclude = $false
    foreach ($pattern in $exclude) {
        if ($file.FullName -like "*$pattern*") {
            $shouldExclude = $true
            break
        }
    }
    -not $shouldExclude
}

Add-Type -Assembly System.IO.Compression.FileSystem
$zipPath = Join-Path $PWD "deploy.zip"
$zip = [System.IO.Compression.ZipFile]::Open($zipPath, 'Create')

foreach ($file in $files) {
    $relativePath = $file.FullName.Substring($PWD.Path.Length + 1)
    $entry = $zip.CreateEntry($relativePath)
    $entryStream = $entry.Open()
    $fileStream = [System.IO.File]::OpenRead($file.FullName)
    $fileStream.CopyTo($entryStream)
    $fileStream.Close()
    $entryStream.Close()
}

$zip.Dispose()

$zipSize = (Get-Item "deploy.zip").Length / 1MB
Write-Host "Created deploy.zip ($([math]::Round($zipSize, 2)) MB)" -ForegroundColor Green

# Wait a moment to ensure any previous deployment is stopped
Write-Host "`nWaiting 10 seconds for any previous deployments to complete..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Deploy using ZIP Deploy
Write-Host "`nDeploying to Azure..." -ForegroundColor Yellow
az webapp deployment source config-zip `
    --resource-group $resourceGroup `
    --name $webAppName `
    --src deploy.zip `
    --timeout 600

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n=== Deployment Successful ===" -ForegroundColor Green
    Write-Host "App URL: https://$webAppName.azurewebsites.net" -ForegroundColor Cyan
    Write-Host "`nWaiting for app to start (this may take 2-3 minutes)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    Write-Host "`nChecking health endpoint..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "https://$webAppName.azurewebsites.net/health" -TimeoutSec 30
        Write-Host "Health check: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "App is still starting up. Check logs in Azure Portal." -ForegroundColor Yellow
    }
} else {
    Write-Host "`n=== Deployment Failed ===" -ForegroundColor Red
    Write-Host "Check the Azure Portal logs for more details." -ForegroundColor Yellow
}

# Cleanup
if (Test-Path "deploy.zip") {
    Remove-Item "deploy.zip" -Force
    Write-Host "`nCleaned up deploy.zip" -ForegroundColor Gray
}
