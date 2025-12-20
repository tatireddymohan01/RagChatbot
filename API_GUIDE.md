# 📖 API Guide - External Application Integration

Complete API reference for integrating the RAG Chatbot with external applications.

## 🌐 Base URLs

```
Local Development:  http://localhost:8000
Production (Azure): https://your-app.azurewebsites.net
```

## 🔑 Authentication

Currently no authentication required. For production, consider adding:
- API keys
- JWT tokens
- OAuth 2.0

## 📚 Interactive Documentation

Visit these URLs when the server is running:

- **Swagger UI** (Interactive testing): `/docs`
- **ReDoc** (Clean documentation): `/redoc`
- **OpenAPI JSON**: `/openapi.json`

---

## API Endpoints

### 1. Health Check

Check if the API is running and get system information.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "RAG Chatbot API",
  "version": "1.0.0",
  "timestamp": "2025-12-20T10:30:00",
  "model": "gpt-4o-mini",
  "embedding_model": "text-embedding-3-small",
  "documents_indexed": 42
}
```

**Examples:**

```bash
# curl
curl http://localhost:8000/health

# PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Python
import requests
response = requests.get("http://localhost:8000/health")
print(response.json())
```

---

### 2. Chat

Send a message and receive an AI-generated response based on your documents.

**Endpoint:** `POST /chat`

**Request Body:**
```json
{
  "query": "What is machine learning?",
  "session_id": "user-123",
  "chat_history": [
    {"role": "user", "content": "Previous question"},
    {"role": "assistant", "content": "Previous answer"}
  ]
}
```

**Parameters:**
- `query` (required, string): The user's question
- `session_id` (optional, string): Unique identifier for conversation session
- `chat_history` (optional, array): Previous conversation turns

**Response:**
```json
{
  "answer": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed...",
  "sources": [
    {
      "content": "Machine learning algorithms build models based on training data...",
      "metadata": {
        "source": "ml_guide.pdf",
        "page": 5
      }
    }
  ],
  "session_id": "user-123"
}
```

**Examples:**

```bash
# curl
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is AI?", "session_id": "user-123"}'

# curl with chat history
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tell me more about it",
    "session_id": "user-123",
    "chat_history": [
      {"role": "user", "content": "What is AI?"},
      {"role": "assistant", "content": "AI stands for Artificial Intelligence..."}
    ]
  }'
```

```powershell
# PowerShell
$body = @{
    query = "What is machine learning?"
    session_id = "user-456"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/chat" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"
```

```python
# Python
import requests

def send_message(query, session_id="user-123", chat_history=None):
    url = "http://localhost:8000/chat"
    payload = {
        "query": query,
        "session_id": session_id
    }
    if chat_history:
        payload["chat_history"] = chat_history
    
    response = requests.post(url, json=payload)
    return response.json()

# Usage
result = send_message("What is deep learning?")
print(f"Answer: {result['answer']}")
print(f"Sources: {len(result['sources'])} documents")
```

```javascript
// JavaScript/Node.js
async function sendMessage(query, sessionId = 'user-123') {
  const response = await fetch('http://localhost:8000/chat', {
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
sendMessage("What is neural network?")
  .then(data => console.log(data.answer));
```

---

### 3. Upload Document (File)

Upload PDF, DOCX, or TXT files for processing.

**Endpoint:** `POST /ingest/file`

**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): The file to upload

**Response:**
```json
{
  "message": "Document processed successfully",
  "filename": "research_paper.pdf",
  "chunks_created": 47,
  "status": "success"
}
```

**Examples:**

```bash
# curl - single file
curl -X POST http://localhost:8000/ingest/file \
  -F "file=@document.pdf"

# curl - from specific path
curl -X POST http://localhost:8000/ingest/file \
  -F "file=@C:/Users/Documents/paper.pdf"
```

```powershell
# PowerShell
$filePath = "C:\Documents\research.pdf"
$form = @{
    file = Get-Item -Path $filePath
}

Invoke-RestMethod -Uri "http://localhost:8000/ingest/file" `
  -Method Post `
  -Form $form
```

```python
# Python
import requests

def upload_file(file_path):
    url = "http://localhost:8000/ingest/file"
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    return response.json()

# Usage
result = upload_file("document.pdf")
print(f"Processed: {result['filename']}")
print(f"Chunks created: {result['chunks_created']}")
```

```javascript
// JavaScript (Browser)
async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:8000/ingest/file', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}

// Usage with file input
document.getElementById('fileInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  const result = await uploadFile(file);
  console.log(`Uploaded: ${result.filename}`);
});
```

```javascript
// Node.js with FormData
const FormData = require('form-data');
const fs = require('fs');

async function uploadFile(filePath) {
  const form = new FormData();
  form.append('file', fs.createReadStream(filePath));
  
  const response = await fetch('http://localhost:8000/ingest/file', {
    method: 'POST',
    body: form,
    headers: form.getHeaders()
  });
  
  return await response.json();
}
```

---

### 4. Ingest from URL

Scrape and process content from a website.

**Endpoint:** `POST /ingest/url`

**Request Body:**
```json
{
  "url": "https://en.wikipedia.org/wiki/Artificial_intelligence"
}
```

**Response:**
```json
{
  "message": "URL content processed successfully",
  "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
  "chunks_created": 89,
  "status": "success"
}
```

**Examples:**

```bash
# curl
curl -X POST http://localhost:8000/ingest/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

```powershell
# PowerShell
$body = @{
    url = "https://en.wikipedia.org/wiki/Machine_learning"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/ingest/url" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"
```

```python
# Python
def ingest_url(url):
    import requests
    response = requests.post(
        "http://localhost:8000/ingest/url",
        json={"url": url}
    )
    return response.json()

# Usage
result = ingest_url("https://docs.python.org/3/tutorial/")
print(f"Processed {result['chunks_created']} chunks from {result['url']}")
```

---

### 5. Ingest Text Directly

Add text content directly without uploading files.

**Endpoint:** `POST /ingest/text`

**Request Body:**
```json
{
  "text": "Your text content here. Can be multiple paragraphs...",
  "metadata": {
    "source": "manual_input",
    "title": "Meeting Notes",
    "date": "2025-12-20"
  }
}
```

**Response:**
```json
{
  "message": "Text processed successfully",
  "chunks_created": 3,
  "status": "success"
}
```

**Examples:**

```bash
# curl
curl -X POST http://localhost:8000/ingest/text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Machine learning is a method of data analysis...",
    "metadata": {"source": "notes", "title": "ML Basics"}
  }'
```

```python
# Python
def ingest_text(text, metadata=None):
    import requests
    payload = {"text": text}
    if metadata:
        payload["metadata"] = metadata
    
    response = requests.post(
        "http://localhost:8000/ingest/text",
        json=payload
    )
    return response.json()

# Usage
text = """
Deep learning is a subset of machine learning.
It uses neural networks with multiple layers.
"""
result = ingest_text(text, {"source": "lecture", "topic": "DL"})
```

---

## 🔄 Session Management

Sessions allow maintaining conversation context across multiple messages.

### How Sessions Work

1. **Each user gets a unique session_id**
2. **Conversation history is stored per session**
3. **Context is maintained across multiple queries**

### Example: Multi-turn Conversation

```python
import requests

API_URL = "http://localhost:8000/chat"
session_id = "user-12345"

def chat(query):
    response = requests.post(API_URL, json={
        "query": query,
        "session_id": session_id
    })
    return response.json()

# Conversation flow
response1 = chat("What is machine learning?")
print(response1["answer"])

# Follow-up question (remembers context)
response2 = chat("What are its applications?")
print(response2["answer"])  # Knows "its" refers to machine learning

# Another follow-up
response3 = chat("Give me an example")
print(response3["answer"])  # Still understands the context
```

### Session Management Best Practices

1. **Generate unique session IDs per user**
```python
import uuid
session_id = str(uuid.uuid4())
```

2. **Clear sessions after inactivity**
```python
# Sessions are automatically managed by the server
# Old sessions are cleaned up based on memory limits
```

3. **Use different sessions for different conversations**
```python
support_session = "support-" + user_id
sales_session = "sales-" + user_id
```

---

## 🌍 Integration Examples

### React Application

```javascript
// ChatService.js
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export class ChatService {
  constructor() {
    this.sessionId = this.generateSessionId();
  }
  
  generateSessionId() {
    return `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
  
  async sendMessage(query) {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: query,
        session_id: this.sessionId
      })
    });
    
    if (!response.ok) {
      throw new Error('Failed to send message');
    }
    
    return await response.json();
  }
  
  async uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}/ingest/file`, {
      method: 'POST',
      body: formData
    });
    
    return await response.json();
  }
  
  async checkHealth() {
    const response = await fetch(`${API_BASE_URL}/health`);
    return await response.json();
  }
}

// Usage in component
import { ChatService } from './ChatService';

function ChatComponent() {
  const [chatService] = useState(() => new ChatService());
  const [messages, setMessages] = useState([]);
  
  const handleSendMessage = async (userMessage) => {
    try {
      const response = await chatService.sendMessage(userMessage);
      setMessages([...messages, 
        { role: 'user', content: userMessage },
        { role: 'assistant', content: response.answer }
      ]);
    } catch (error) {
      console.error('Error:', error);
    }
  };
  
  return (
    // Your chat UI here
  );
}
```

### Vue.js Application

```javascript
// chatApi.js
export default {
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:8000',
  sessionId: `user-${Date.now()}`,
  
  async chat(query) {
    const response = await fetch(`${this.baseURL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query,
        session_id: this.sessionId
      })
    });
    return await response.json();
  },
  
  async uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${this.baseURL}/ingest/file`, {
      method: 'POST',
      body: formData
    });
    return await response.json();
  }
};
```

### Python Flask/Django Backend

```python
# backend_service.py
import requests
from typing import List, Dict

class RAGChatbotClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def chat(self, query: str, session_id: str, 
             chat_history: List[Dict] = None) -> Dict:
        """Send a chat message"""
        payload = {
            "query": query,
            "session_id": session_id
        }
        if chat_history:
            payload["chat_history"] = chat_history
        
        response = self.session.post(
            f"{self.base_url}/chat",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def upload_document(self, file_path: str) -> Dict:
        """Upload a document for processing"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = self.session.post(
                f"{self.base_url}/ingest/file",
                files=files
            )
        response.raise_for_status()
        return response.json()
    
    def ingest_url(self, url: str) -> Dict:
        """Ingest content from URL"""
        response = self.session.post(
            f"{self.base_url}/ingest/url",
            json={"url": url}
        )
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

# Usage
client = RAGChatbotClient("https://your-app.azurewebsites.net")

# Send message
result = client.chat("What is AI?", session_id="user-123")
print(result["answer"])

# Upload document
upload_result = client.upload_document("document.pdf")
print(f"Processed: {upload_result['chunks_created']} chunks")
```

### Mobile App (React Native)

```javascript
// ChatAPI.js
const API_BASE_URL = 'https://your-app.azurewebsites.net';

export const ChatAPI = {
  async sendMessage(query, sessionId) {
    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          session_id: sessionId
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },
  
  async uploadDocument(uri, fileName) {
    const formData = new FormData();
    formData.append('file', {
      uri: uri,
      type: 'application/pdf',
      name: fileName
    });
    
    const response = await fetch(`${API_BASE_URL}/ingest/file`, {
      method: 'POST',
      body: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    });
    
    return await response.json();
  }
};
```

---

## ⚠️ Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request parameters |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Example Error Handling

```python
import requests

def safe_chat(query, session_id):
    try:
        response = requests.post(
            "http://localhost:8000/chat",
            json={"query": query, "session_id": session_id},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.Timeout:
        print("Request timed out")
        return None
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code}")
        print(f"Detail: {e.response.json().get('detail', 'Unknown error')}")
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
```

```javascript
// JavaScript
async function safeChat(query, sessionId) {
  try {
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, session_id: sessionId })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Request failed');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Chat error:', error.message);
    return null;
  }
}
```

---

## 🔐 CORS Configuration

By default, CORS is enabled for all origins (`*`). For production, configure specific origins:

```env
# .env
CORS_ORIGINS=["https://your-frontend.com", "https://app.example.com"]
```

---

## 💡 Best Practices

1. **Use Unique Session IDs**
   - Generate per user: `user-${userId}-${timestamp}`
   - Maintain across app session

2. **Handle Timeouts**
   - Set reasonable timeouts (30s for chat, 60s for uploads)
   - Show loading indicators

3. **Validate Inputs**
   - Check file types before upload
   - Validate URLs
   - Limit message length

4. **Error Recovery**
   - Implement retry logic
   - Show user-friendly error messages
   - Log errors for debugging

5. **Performance**
   - Cache health check results
   - Debounce rapid API calls
   - Use connection pooling

---

## 📞 Support

- Issues: GitHub Issues
- Documentation: [README.md](README.md) | [PROJECT_GUIDE.md](PROJECT_GUIDE.md)
- Interactive Testing: `/docs` endpoint

---

**Happy Integrating! 🚀**
