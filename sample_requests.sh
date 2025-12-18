# Sample cURL Requests for RAG Chatbot API

## Health Check
curl http://localhost:8000/health

## Root Endpoint
curl http://localhost:8000/

## 1. Ingest Documents (PDF, DOCX, TXT)
# Single file
curl -X POST "http://localhost:8000/ingest/docs" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@/path/to/document.pdf"

# Multiple files
curl -X POST "http://localhost:8000/ingest/docs" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@document1.pdf" \
  -F "files=@document2.docx" \
  -F "files=@document3.txt"

## 2. Ingest from URL
curl -X POST "http://localhost:8000/ingest/url" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://en.wikipedia.org/wiki/Machine_learning"}'

# Another example
curl -X POST "http://localhost:8000/ingest/url" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://en.wikipedia.org/wiki/Artificial_intelligence"}'

## 3. Chat - Simple Query
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is machine learning?"}'

## 4. Chat - With Session ID
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is deep learning?","session_id":"user-123"}'

## 5. Chat - With History
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tell me more about neural networks",
    "session_id": "user-123",
    "chat_history": [
      {"role": "user", "content": "What is deep learning?"},
      {"role": "assistant", "content": "Deep learning is a subset of machine learning that uses neural networks with multiple layers."}
    ]
  }'

## 6. Follow-up Question (using same session_id)
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query":"Can you explain that in simpler terms?","session_id":"user-123"}'

## Windows PowerShell Examples

# Health Check
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get

# Ingest Document
$form = @{
    files = Get-Item -Path "C:\path\to\document.pdf"
}
Invoke-RestMethod -Uri "http://localhost:8000/ingest/docs" -Method Post -Form $form

# Ingest URL
$body = @{
    url = "https://en.wikipedia.org/wiki/Machine_learning"
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/ingest/url" -Method Post -Body $body -ContentType "application/json"

# Chat
$body = @{
    query = "What is machine learning?"
    session_id = "user-123"
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -Body $body -ContentType "application/json"

# Chat with History
$body = @{
    query = "Tell me more about that"
    session_id = "user-123"
    chat_history = @(
        @{role = "user"; content = "What is AI?"},
        @{role = "assistant"; content = "AI is artificial intelligence..."}
    )
} | ConvertTo-Json -Depth 10
Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -Body $body -ContentType "application/json"
