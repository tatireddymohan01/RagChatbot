# 📝 Chatbot Integration Steps

## 1. **Prepare the Required Files**

Copy these files from your project to your website’s static/assets folder:
- `widget.css`  →  All widget styles
- `script_widget.js`  →  All widget functionality

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
