# Quick Start: Testing the Sitemap Crawler Feature

## What Was Added

A new **cloud-native URL discovery endpoint** that parses sitemap.xml files and automatically ingests all discovered URLs without requiring ChromeDriver. Perfect for Azure, AWS Lambda, and serverless deployments.

## Key Changes

### 1. New Service: Sitemap Crawler
- **File**: `app/services/sitemap_crawler.py`
- **What it does**: Fetches and parses sitemap.xml files, extracts all URLs
- **Cloud-friendly**: No Chrome/Chromium needed

### 2. New API Endpoint
- **Route**: `POST /ingest/sitemap`
- **Input**: `{"domain": "example.com"}`
- **Output**: Discovered and ingested URLs with statistics

### 3. New Admin UI Card
- **Location**: Admin console at `/admin`
- **Card**: 🗺️ Sitemap (green-themed, between URL Cleanup and Files)
- **Features**: Domain input, progress display, results summary

## Testing Steps

### Local Testing

#### Step 1: Start the Application
```bash
cd d:\GitHubRepos\GenAI\RagChatbot
python app/main.py
```

#### Step 2: Open Admin Console
Navigate to: `http://localhost:8000/admin`

#### Step 3: Find the Sitemap Card
Scroll down and locate the **🗺️ Sitemap** card (green border)

#### Step 4: Test with Example Domain
1. Click in the domain field
2. Enter: `www.alchemindssolutions.com` (or any domain with sitemap.xml)
3. Click "Ingest from Sitemap" button
4. Watch progress messages appear
5. View results showing:
   - URLs discovered
   - URLs successfully ingested
   - Total chunks created
   - List of ingested sources

### API Testing (cURL)

```bash
# Test sitemap discovery and ingestion
curl -X POST http://localhost:8000/ingest/sitemap \
  -H "Content-Type: application/json" \
  -d '{"domain": "www.alchemindssolutions.com"}'

# Example response:
{
  "status": "success",
  "message": "Ingested 15/20 URLs from sitemap",
  "documents_processed": 15,
  "chunks_created": 342,
  "sources": [
    "https://www.alchemindssolutions.com/",
    "https://www.alchemindssolutions.com/about",
    ...
  ]
}
```

### Python Testing

```python
import requests

# Ingest from sitemap
response = requests.post(
    'http://localhost:8000/ingest/sitemap',
    json={'domain': 'www.example.com'}
)

result = response.json()
print(f"Status: {result['status']}")
print(f"Chunks created: {result['chunks_created']}")
print(f"URLs ingested: {result['documents_processed']}")
```

### Verification Query

After ingestion, test in chat to verify content is available:

**Admin Console Chat Tab:**
1. Go to "Chat" card at top
2. Enter query: "What is [company/topic name from ingested domain]?"
3. Should return relevant information from ingested pages

## Expected Behavior

### Success Scenario ✅
```
Discovering URLs from sitemap...
(This may take a moment)

status: "success"
message: "Ingested 42/50 URLs from sitemap"
documents_processed: 42
chunks_created: 1,234
```

### Partial Success (Some URLs Failed)
```
status: "partial"
message: "Ingested 38/50 URLs from sitemap"
documents_processed: 38
chunks_created: 1,100
(Note: Shows which URLs were skipped in logs)
```

### Error: Missing Sitemap
```
Error: No URLs found in sitemap for example.com
(Verify the domain has a sitemap.xml at /sitemap.xml)
```

## Comparison: Old vs New

| Feature | Before | After |
|---------|--------|-------|
| **Cloud Support** | ❌ Requires ChromeDriver | ✅ Pure Python, no browser |
| **URL Discovery** | Manual input only | ✅ Auto-discover via sitemap.xml |
| **Azure Compatibility** | ❌ Full Site mode fails | ✅ Works on all cloud platforms |
| **Deployment** | Needs Chrome container | ✅ Standard Python runtime |
| **Speed** | Slow (page rendering) | ✅ Fast (XML parsing) |

## Troubleshooting

### Issue: "No URLs found in sitemap"
**Solution**: Verify the domain has sitemap.xml at:
- `https://example.com/sitemap.xml`
- `https://example.com/sitemap.xml.gz`
- Or check robots.txt for sitemap location

### Issue: "Only ingested 5/50 URLs"
**Solution**: Some URLs may have failed scraping. Check logs for:
- Network timeouts
- 404/403 errors
- Page loading issues
- Try again (intermittent failures are normal)

### Issue: Results show 0 chunks created
**Solution**: 
- Verify URLs contain text content
- Check if pages require JavaScript (simple scraper might not render)
- Try ingesting via Single URLs mode to debug

### Issue: Chat doesn't find ingested content
**Solution**:
- Confirm chunks_created > 0 in sitemap response
- Try /health endpoint to verify vectorstore is working
- Search for very specific phrases from ingested pages

## For Azure Cloud Deployment

1. **Update code** to latest version with sitemap feature
2. **Deploy** to Azure App Service as normal
3. **Verify** in `/health` endpoint that `full_site_scraping: false` (expected)
4. **Use** the Sitemap card in admin console instead of Full Site mode
5. **Monitor** Application Insights logs for any errors

## Files to Know

- **Service**: `app/services/sitemap_crawler.py` - The parsing logic
- **Endpoint**: `app/api/ingest.py` (search for "ingest_from_sitemap") - API implementation
- **Admin UI**: `ui/templates/admin.html` (search for "sitemapBtn") - Frontend card
- **Docs**: `SITEMAP_FEATURE.md` - Detailed documentation

## Next Steps

1. ✅ Test locally with example domains
2. ✅ Verify admin console UI works
3. ✅ Test chat queries with ingested content
4. ✅ Deploy to Azure and test there
5. ✅ Update PROJECT_GUIDE.md with new feature

## Performance Notes

- **Sitemap parsing**: < 1 second
- **Per-URL scraping**: ~2-5 seconds each
- **100 URLs**: ~5-8 minutes total
- **Vectorization**: Automatic via LangChain

Larger sites with hundreds of URLs may take 30+ minutes. Monitor logs for progress.

---

**Ready to test?** Start the app and navigate to `/admin` → Scroll to 🗺️ Sitemap card!
