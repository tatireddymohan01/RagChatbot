# Azure Deployment - Pricing Tiers

## Available Options

### 🆓 F1 - Free Tier (Default)
**Cost:** FREE
**Specs:**
- 1 GB RAM
- 1 GB Storage
- 60 CPU minutes/day
- Shared compute
- Apps sleep after 20 mins inactivity
- No custom domains
- No SSL certificates

**Best for:** Testing, demos, learning

**Usage:**
```powershell
.\deploy-azure.ps1
# or explicitly
.\deploy-azure.ps1 -AppServiceSku "F1"
```

---

### 💰 B1 - Basic Tier
**Cost:** ~$13/month
**Specs:**
- 1.75 GB RAM
- 10 GB Storage
- Unlimited CPU time
- Dedicated compute
- Always-on (no sleep)
- Custom domains
- SSL certificates

**Best for:** Small production apps, personal projects

**Usage:**
```powershell
.\deploy-azure.ps1 -AppServiceSku "B1"
```

---

### 🚀 S1 - Standard Tier
**Cost:** ~$70/month
**Specs:**
- 1.75 GB RAM
- 50 GB Storage
- Unlimited CPU time
- Dedicated compute
- Auto-scaling (up to 10 instances)
- Staging slots
- Daily backups

**Best for:** Production apps with traffic

**Usage:**
```powershell
.\deploy-azure.ps1 -AppServiceSku "S1"
```

---

### 🏢 P1v2 - Premium Tier
**Cost:** ~$150/month
**Specs:**
- 3.5 GB RAM
- 250 GB Storage
- Faster CPU
- Auto-scaling (up to 30 instances)
- Advanced features

**Best for:** High-traffic production apps

**Usage:**
```powershell
.\deploy-azure.ps1 -AppServiceSku "P1v2"
```

---

## Comparison Table

| Feature | F1 (Free) | B1 (Basic) | S1 (Standard) | P1v2 (Premium) |
|---------|-----------|------------|---------------|----------------|
| **Cost/month** | $0 | $13 | $70 | $150 |
| **RAM** | 1 GB | 1.75 GB | 1.75 GB | 3.5 GB |
| **Storage** | 1 GB | 10 GB | 50 GB | 250 GB |
| **CPU Limit** | 60 min/day | Unlimited | Unlimited | Unlimited |
| **Always On** | ❌ | ✅ | ✅ | ✅ |
| **Auto Scale** | ❌ | ❌ | ✅ | ✅ |
| **Custom Domain** | ❌ | ✅ | ✅ | ✅ |
| **SSL** | ❌ | ✅ | ✅ | ✅ |
| **Staging Slots** | ❌ | ❌ | ✅ | ✅ |
| **Daily Backups** | ❌ | ❌ | ✅ | ✅ |

---

## Additional Costs

### Azure Container Registry (ACR)
- **Basic:** $5/month (10 GB storage)
- **Standard:** $20/month (100 GB storage)
- **Premium:** $100/month (500 GB storage)

**Note:** All deployment scripts use Basic ACR by default (~$5/month)

---

## Total Monthly Costs

| Tier | App Service | ACR | **Total** |
|------|-------------|-----|-----------|
| F1 (Free) | $0 | $5 | **$5/month** |
| B1 (Basic) | $13 | $5 | **$18/month** |
| S1 (Standard) | $70 | $5 | **$75/month** |
| P1v2 (Premium) | $150 | $5 | **$155/month** |

---

## Recommendations

### 🎓 Learning/Testing
```powershell
.\deploy-azure.ps1  # Uses F1 free tier
```
**Cost:** $5/month (ACR only)

### 🏠 Personal Projects
```powershell
.\deploy-azure.ps1 -AppServiceSku "B1"
```
**Cost:** $18/month

### 💼 Small Business
```powershell
.\deploy-azure.ps1 -AppServiceSku "S1"
```
**Cost:** $75/month

### 🏢 Production/Enterprise
```powershell
.\deploy-azure.ps1 -AppServiceSku "P1v2"
```
**Cost:** $155/month

---

## Free Tier Limitations

⚠️ **Important:** The F1 free tier has these limitations:

1. **60 CPU minutes/day limit**
   - Counter resets at midnight UTC
   - App stops when limit reached
   - Ideal for demos and testing

2. **Apps sleep after 20 minutes of inactivity**
   - First request after sleep takes 10-15 seconds
   - Subsequent requests are fast
   - Not suitable for time-sensitive apps

3. **Shared compute**
   - Resources shared with other users
   - Performance can vary

4. **No custom domains or SSL**
   - Must use *.azurewebsites.net domain

5. **No always-on**
   - Background tasks won't run when app is asleep

---

## Upgrading Your App

To upgrade an existing deployment:

```powershell
# Upgrade to Basic tier
az appservice plan update `
  --name plan-ragchatbot `
  --resource-group rg-ragchatbot `
  --sku B1

# Upgrade to Standard tier
az appservice plan update `
  --name plan-ragchatbot `
  --resource-group rg-ragchatbot `
  --sku S1
```

Or redeploy with new SKU:
```powershell
.\deploy-azure.ps1 -AppServiceSku "B1" -SkipResourceCreation
```

---

## Cost Optimization Tips

1. **Use F1 for development/testing**
   - Deploy production on B1 or higher

2. **Delete resources when not in use**
   ```powershell
   .\cleanup-azure.ps1
   ```

3. **Monitor usage**
   ```bash
   az monitor metrics list --resource-group rg-ragchatbot
   ```

4. **Set up cost alerts**
   - Go to Azure Portal → Cost Management + Billing → Budgets

5. **Use Azure Cost Calculator**
   - https://azure.microsoft.com/pricing/calculator/

---

## Free Azure Credits

### Students
- **$100 credit** free for students
- No credit card required
- https://azure.microsoft.com/free/students/

### New Users
- **$200 credit** for 30 days
- 12 months of free services
- https://azure.microsoft.com/free/

---

For current pricing, visit: https://azure.microsoft.com/pricing/details/app-service/
