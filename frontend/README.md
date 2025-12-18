# RAG Chatbot Frontend

Standalone frontend for the RAG Chatbot API. Can be deployed independently to any static hosting service.

## Features

- ✨ Modern, professional UI design
- 📱 Fully responsive (mobile, tablet, desktop)
- 🎨 Smooth animations and transitions
- 🔔 Toast notifications for user feedback
- 📊 Live statistics (documents, messages)
- 🌐 Configurable API endpoint
- 🚀 Zero dependencies (vanilla JavaScript)

## Quick Start

### 1. Configure API Endpoint

Edit `config.js` to point to your API server:

```javascript
const CONFIG = {
    // Your API endpoint
    API_BASE_URL: 'http://localhost:8000',
    
    // Or production URL
    // API_BASE_URL: 'https://your-api.azurewebsites.net',
    
    TIMEOUT: 60000,
    DEBUG: false
};
```

### 2. Run Locally

**Option A: Python**
```bash
python -m http.server 3000
```

**Option B: Node.js**
```bash
npx http-server -p 3000
```

**Option C: PHP**
```bash
php -S localhost:3000
```

Then open: `http://localhost:3000`

### 3. Deploy to Production

See deployment options below.

## Files

```
frontend/
├── index.html      # Main HTML structure
├── style.css       # Styles and animations
├── script.js       # Frontend logic
├── config.js       # API configuration (EDIT THIS!)
└── README.md       # This file
```

## Deployment Options

### GitHub Pages

1. Create a new repository
2. Upload frontend files
3. Enable GitHub Pages in settings
4. Access at: `https://username.github.io/repo-name`

### Netlify

1. Sign up at [netlify.com](https://netlify.com)
2. Drag and drop this folder
3. Or connect to Git repository
4. Configure build settings (none required for static sites)

**CLI Deployment:**
```bash
npm install -g netlify-cli
netlify deploy --prod
```

### Vercel

1. Sign up at [vercel.com](https://vercel.com)
2. Install CLI: `npm install -g vercel`
3. Deploy:

```bash
vercel --prod
```

### Azure Static Web Apps

```bash
az staticwebapp create \
  --name rag-chatbot-frontend \
  --resource-group your-rg \
  --source .
```

### AWS S3 + CloudFront

```bash
# Create bucket
aws s3 mb s3://rag-chatbot-frontend

# Enable static hosting
aws s3 website s3://rag-chatbot-frontend \
  --index-document index.html

# Upload files
aws s3 sync . s3://rag-chatbot-frontend/ \
  --exclude ".git/*"

# Access at bucket URL or setup CloudFront for HTTPS
```

### Firebase Hosting

```bash
npm install -g firebase-tools
firebase login
firebase init hosting
firebase deploy
```

## Configuration

### API Endpoint

Update `config.js` with your API URL:

```javascript
// Development
API_BASE_URL: 'http://localhost:8000'

// Production
API_BASE_URL: 'https://your-api-domain.com'

// Same domain (if deployed together)
API_BASE_URL: window.location.origin
```

### Debug Mode

Enable debug logging:

```javascript
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
    DEBUG: true  // Enable console logging
};
```

## API Requirements

The backend API must:

1. **Enable CORS** for your frontend domain
2. **Run API-only mode** (optional but recommended)
3. **Have proper endpoints** (see API_DOCUMENTATION.md)

### Backend Configuration

In your backend `.env` file:

```env
# Enable API-only mode (no UI from backend)
API_ONLY=true

# Allow your frontend domain
CORS_ORIGINS=["https://your-frontend-domain.com", "http://localhost:3000"]
```

## Features

### Document Management
- Upload PDF, DOCX, TXT files
- Ingest content from URLs
- Real-time processing feedback

### Chat Interface
- Natural language queries
- Context-aware responses
- Conversation history
- Clean message display (sources hidden by default)

### System Monitoring
- API health status
- Live document counter
- Message counter
- Connection status indicator

## Browser Support

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers

## Troubleshooting

### "Unable to connect to API"

**Cause:** API is not running or URL is incorrect

**Solution:**
1. Verify API is running: `curl http://your-api-url/health`
2. Check `config.js` has correct `API_BASE_URL`
3. Check browser console for errors

### CORS Error

**Cause:** Backend not allowing your frontend domain

**Solution:**
1. Add your domain to backend `CORS_ORIGINS`
2. Restart backend
3. Clear browser cache

### Files not uploading

**Cause:** API endpoint incorrect or file too large

**Solution:**
1. Check API URL in `config.js`
2. Verify `/ingest/docs` endpoint exists
3. Check file size limits (backend configuration)

### Blank responses

**Cause:** No documents ingested

**Solution:**
1. Upload documents first
2. Or enable `ALLOW_GENERAL_KNOWLEDGE=true` in backend

## Customization

### Colors

Edit `style.css` CSS variables:

```css
:root {
    --primary-color: #6366f1;
    --secondary-color: #8b5cf6;
    --success-color: #10b981;
    --danger-color: #ef4444;
    /* ... more colors */
}
```

### Layout

Modify `index.html` structure as needed. The UI uses CSS Grid and Flexbox for responsive layout.

### Branding

Update logo and title:
1. Change `<title>` in `index.html`
2. Modify logo SVG or replace with image
3. Update text in header section

## Development

### Local Testing with API

1. Start backend:
```bash
cd ..
docker-compose up -d
```

2. Update config:
```javascript
API_BASE_URL: 'http://localhost:8000'
DEBUG: true
```

3. Start frontend:
```bash
python -m http.server 3000
```

4. Test at: `http://localhost:3000`

### Code Structure

**index.html**
- Semantic HTML5 structure
- Accessibility features (ARIA labels)
- Responsive meta tags

**style.css**
- CSS variables for theming
- Mobile-first responsive design
- Smooth animations
- Modern shadow system

**script.js**
- Modular functions
- Error handling
- XSS prevention (escapeHtml)
- Auto-resize textarea
- Toast notifications

**config.js**
- Centralized configuration
- Easy deployment updates
- Environment detection

## Security

### XSS Prevention

All user input is escaped using `escapeHtml()` function before rendering.

### CORS

Frontend makes cross-origin requests. Ensure backend CORS is properly configured.

### HTTPS

Always use HTTPS in production:
- Protects API keys
- Secures data transmission
- Required for modern browser features

## Performance

### Optimization Tips

1. **Use CDN** for static assets (if adding libraries)
2. **Enable compression** on hosting platform
3. **Lazy load** images (if adding)
4. **Minify** CSS/JS for production
5. **Cache** API responses when appropriate

### Bundle Size

Current bundle: **~15KB** (uncompressed)
- No external dependencies
- Pure vanilla JavaScript
- Lightweight and fast

## License

Same license as the main RAG Chatbot project.

## Support

For API integration issues, see:
- [API Documentation](../API_DOCUMENTATION.md)
- [Separated Architecture Guide](../SEPARATED_ARCHITECTURE.md)
- [Main README](../README.md)

---

**Ready to deploy!** 🚀
