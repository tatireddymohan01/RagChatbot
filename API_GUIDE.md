# 📖 API & Integration Guide

Complete reference for integrating the RAG Chatbot API with any frontend or application.

## 🌐 API Endpoints

### Base URL
```
http://localhost:8000  # Local development
https://your-app.azurewebsites.net  # Production
```

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "RAG Chatbot API",
  "version": "1.0.0",
  "timestamp": "2025-12-19T10:30:00",
  "model": "gpt-4o-mini"
}
```

### Chat
```http
POST /chat
Content-Type: application/json

{
  "query": "What is machine learning?",
  "session_id": "user-123",
  "chat_history": []
}
```

**Response:**
```json
{
  "answer": "Machine learning is...",
  "sources": [
    {
      "content": "Relevant document excerpt",
      "metadata": {"source": "document.pdf", "page": 1}
    }
  ],
  "session_id": "user-123"
}
```

### Document Ingestion

**Text:**
```http
POST /ingest/text
Content-Type: application/json

{
  "text": "Your text content here",
  "metadata": {"source": "manual_input"}
}
```

**File Upload:**
```http
POST /ingest/file
Content-Type: multipart/form-data

file: <PDF/DOCX/TXT file>
```

**URL:**
```http
POST /ingest/url
Content-Type: application/json

{
  "url": "https://example.com/article"
}
```

---

## 💻 Integration Examples

### JavaScript/React

```javascript
const API_URL = 'http://localhost:8000';

// Chat function
async function sendMessage(query, sessionId) {
  const response = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      session_id: sessionId
    })
  });
  
  return await response.json();
}

// Usage
const result = await sendMessage('What is AI?', 'user-123');
console.log(result.answer);
```

### Python

```python
import requests

API_URL = 'http://localhost:8000'

def send_message(query: str, session_id: str = None):
    response = requests.post(
        f'{API_URL}/chat',
        json={
            'query': query,
            'session_id': session_id
        }
    )
    return response.json()

# Usage
result = send_message('What is AI?', 'user-123')
print(result['answer'])
```

### cURL

```bash
# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?"}'

# Ingest text
curl -X POST http://localhost:8000/ingest/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Machine learning is a subset of AI..."}'

# Upload file
curl -X POST http://localhost:8000/ingest/file \
  -F "file=@document.pdf"
```

### Node.js

```javascript
const axios = require('axios');

const API_URL = 'http://localhost:8000';

async function chat(query, sessionId) {
  const response = await axios.post(`${API_URL}/chat`, {
    query: query,
    session_id: sessionId
  });
  
  return response.data;
}

// Usage
chat('What is AI?', 'user-123')
  .then(result => console.log(result.answer))
  .catch(error => console.error(error));
```

---

## 🎨 Frontend Integration Patterns

### React Example

```jsx
import { useState, useEffect } from 'react';

function ChatComponent() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const API_URL = 'http://localhost:8000';

  const sendMessage = async () => {
    if (!message.trim()) return;

    // Add user message
    setMessages(prev => [...prev, { 
      role: 'user', 
      content: message 
    }]);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: message })
      });

      const data = await response.json();
      
      // Add AI response
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.answer 
      }]);
    } catch (error) {
      console.error('Error:', error);
    }

    setMessage('');
  };

  return (
    <div>
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={msg.role}>
            {msg.content}
          </div>
        ))}
      </div>
      <input 
        value={message}
        onChange={e => setMessage(e.target.value)}
        onKeyPress={e => e.key === 'Enter' && sendMessage()}
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}
```

### Vue.js Example

```vue
<template>
  <div>
    <div v-for="msg in messages" :key="msg.id" :class="msg.role">
      {{ msg.content }}
    </div>
    <input v-model="message" @keyup.enter="sendMessage" />
    <button @click="sendMessage">Send</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      message: '',
      messages: [],
      apiUrl: 'http://localhost:8000'
    };
  },
  methods: {
    async sendMessage() {
      if (!this.message.trim()) return;

      this.messages.push({ 
        role: 'user', 
        content: this.message 
      });

      try {
        const response = await fetch(`${this.apiUrl}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: this.message })
        });

        const data = await response.json();
        this.messages.push({ 
          role: 'assistant', 
          content: data.answer 
        });
      } catch (error) {
        console.error('Error:', error);
      }

      this.message = '';
    }
  }
};
</script>
```

---

## ⚙️ Configuration

### CORS Setup

For production with external frontend:

```python
# In .env
CORS_ORIGINS=["https://your-frontend.com", "https://app.example.com"]
```

### API-Only Mode

To disable the built-in UI:

```python
# In .env
API_ONLY=true
```

---

## 🔐 Authentication (Optional)

To add authentication, you can extend the API:

```python
from fastapi import Header, HTTPException

async def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    # Add your token verification logic
    return True

# Use in endpoints
@router.post("/chat", dependencies=[Depends(verify_token)])
async def chat(request: ChatRequest):
    # Your chat logic
```

---

## 📊 Rate Limiting

Example using slowapi:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, chat_request: ChatRequest):
    # Your chat logic
```

---

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Test specific endpoint
pytest tests/test_chat.py -v

# With coverage
pytest --cov=app tests/
```

---

## 📚 OpenAPI Documentation

Access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 🎯 Best Practices

1. **Always use session_id** for conversation context
2. **Handle errors gracefully** on the frontend
3. **Show loading states** during API calls
4. **Implement retry logic** for failed requests
5. **Cache responses** when appropriate
6. **Validate inputs** before sending to API
7. **Use environment variables** for API URL
8. **Implement proper error handling**

---

## 🆘 Troubleshooting

### CORS Errors
- Check `CORS_ORIGINS` in `.env`
- Ensure frontend URL is in allowed origins

### 404 Not Found
- Verify endpoint URL is correct
- Check if API server is running
- Ensure no typos in route paths

### 500 Internal Server Error
- Check API logs: `docker-compose logs -f`
- Verify OpenAI API key is valid
- Ensure documents are ingested

### Slow Responses
- Consider using streaming responses
- Optimize document chunk size
- Use faster embedding models
- Enable caching
