# 🚀 RAG Chatbot Embed Guide

## Quick Start - One-Line Embed

The RAG Chatbot uses a modern **one-line embed** approach - no files to copy, no configuration hassles!

### Step 1: Deploy to Azure

Deploy your RAG Chatbot backend to Azure App Service:
```
https://your-ragchatbot.azurewebsites.net
```

### Step 2: Add to Any Website

Simply add **one line** to your website's HTML, just before the closing `</body>` tag:

```html
<script src="https://your-ragchatbot.azurewebsites.net/static/embed.js"></script>
```

That's it! The floating chat bubble will appear automatically.

### Step 3: (Optional) Customize

Add configuration before the embed script to customize appearance and behavior:

```html
<script>
    window.RagChatbotConfig = {
        apiUrl: 'https://your-ragchatbot.azurewebsites.net',
        position: 'bottom-right',
        primaryColor: '#4285f4',
        title: 'AI Assistant',
        welcomeMessage: '👋 Hello! How can I help you today?'
    };
</script>
<script src="https://your-ragchatbot.azurewebsites.net/static/embed.js"></script>
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiUrl` | string | `window.location.origin` | Your RAG Chatbot backend URL |
| `position` | string | `'bottom-right'` | Widget position: `'bottom-right'`, `'bottom-left'`, `'top-right'`, `'top-left'` |
| `primaryColor` | string | `'#4285f4'` | Primary color for the widget header and buttons |
| `title` | string | `'AI Assistant'` | Widget header title |
| `welcomeMessage` | string | `'👋 Hello!'` | Initial welcome message |

## Complete Example

Here's a complete example for embedding on an external website:

```html
<!DOCTYPE html>
<html>
<head>
    <title>My Business Website</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to My Business</h1>
        <p>We've integrated an AI chatbot to answer your questions. Click the floating button in the bottom-right corner!</p>
    </div>

    <!-- RAG Chatbot Configuration -->
    <script>
        window.RagChatbotConfig = {
            apiUrl: 'https://your-ragchatbot.azurewebsites.net',
            position: 'bottom-right',
            primaryColor: '#4285f4',
            title: 'Support Assistant',
            welcomeMessage: '👋 Hello! Ask me anything about our services.'
        };
    </script>

    <!-- One-Line Embed Loader -->
    <script src="https://your-ragchatbot.azurewebsites.net/static/embed.js"></script>
</body>
</html>
```

## How It Works

1. **embed.js** - A lightweight loader that:
   - Reads your configuration
   - Creates the widget HTML dynamically
   - Loads the CSS styles from your server
   - Injects the interactive JavaScript

2. **No File Copies** - Everything is hosted on your Azure server

3. **Instant Updates** - Change styling/behavior once, updates everywhere

4. **CORS Enabled** - Works on any domain without issues

## Features

✅ **Floating Bubble** - Animated chat bubble that stands out
✅ **Resizable Window** - Users can resize to their preference
✅ **Clean Design** - Professional Google-style interface
✅ **Mobile Responsive** - Works on all devices
✅ **Source Citations** - Answers include document sources
✅ **Session Memory** - Maintains conversation context
✅ **One-Line Setup** - No complex integration needed

## Troubleshooting

### Widget Not Appearing
- Ensure your Azure URL is correct and accessible
- Check browser console for errors (F12 → Console)
- Verify CORS is enabled in your FastAPI app

### API Connection Errors
- Confirm `apiUrl` in config matches your Azure deployment
- Check that your backend is running
- Verify the `/chat` endpoint is working

### Styling Issues
- Clear browser cache (Ctrl+Shift+Delete)
- Check that `primaryColor` is a valid hex color
- Ensure your CSS is loading from the correct path

## Security Considerations

✅ Use HTTPS for your Azure deployment
✅ Enable CORS only for trusted domains if needed
✅ Store API keys securely in Azure Key Vault
✅ Monitor API usage and rate limiting
✅ Keep your backend dependencies updated

## Local Testing

Before deploying to Azure, test locally:

```bash
# Start local server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Use in test HTML
<script>
    window.RagChatbotConfig = {
        apiUrl: 'http://localhost:8000'
    };
</script>
<script src="http://localhost:8000/static/embed.js"></script>
```

---

## Support

For issues or questions, check:

- [README.md](README.md) - Project overview
- Server logs for backend errors
- Browser console (F12) for frontend errors
- Azure Application Insights for production monitoring

---

**Happy chatting! 🤖✨**

## 2. **Add the Widget HTML to Your Webpage**

Paste the following HTML just before your closing `</body>` tag:
```html
<!-- Chatbot Widget Start -->
<button id="chatBubble" class="chat-bubble" aria-label="Open chat">
  <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="12" r="12" fill="#06b6d4"/>
    <path d="M7 10h10M7 14h6" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
  </svg>
</button>
<div id="chatWidget" class="chat-widget" style="display:none;">
  <div class="widget-header">
    <span class="widget-title">AI Chat Assistant</span>
    <button id="minimizeWidget" class="widget-btn" aria-label="Minimize">—</button>
    <button id="closeWidget" class="widget-btn" aria-label="Close">×</button>
  </div>
  <div class="chat-area" id="chatArea">
    <div class="welcome-message">👋 Hello! How can I help you today?</div>
  </div>
  <form id="chatForm" class="chat-form">
    <textarea id="chatInput" class="chat-input" placeholder="Type your message..." rows="1"></textarea>
    <button type="submit" id="sendBtn" class="send-btn" aria-label="Send">➤</button>
  </form>
</div>
<!-- Chatbot Widget End -->
```

## 3. **Link the CSS and JS Files**

In your `<head>` section, add:
```html
<link rel="stylesheet" href="path/to/widget.css">
```
Before your closing `</body>` tag, add:
```html
<script src="path/to/script_widget.js"></script>
```
Replace `path/to/` with the actual path where you placed the files.

## 4. **Configure the API Endpoint**

Open `script_widget.js` and set your API base URL at the top:
```js
const API_BASE_URL = "https://your-api-domain.com"; // Update this to your backend URL
```

## 5. **Test the Integration**

- Open your website in a browser.
- You should see a floating chat bubble in the bottom-right corner.
- Click the bubble to open the chat widget and start chatting!

---

## ✅ **Summary**

- Copy `widget.css` and `script_widget.js` to your site.
- Add the provided HTML for the chat widget.
- Link the CSS/JS files.
- Set your API endpoint in the JS file.
- Test and enjoy your embedded chatbot!
