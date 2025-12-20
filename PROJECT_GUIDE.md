# 🔍 Project Guide - Technical Deep Dive

Complete technical documentation explaining how every component works in the RAG Chatbot.

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Data Flow](#data-flow)
4. [Code Structure](#code-structure)
5. [Technologies Used](#technologies-used)
6. [How RAG Works](#how-rag-works)
7. [Component Details](#component-details)

---

## Architecture Overview

The RAG Chatbot follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (UI)                       │
│              HTML + CSS + JavaScript                    │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTP/REST API
┌──────────────────▼──────────────────────────────────────┐
│                  FastAPI Server                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │         API Layer (Routers)                      │  │
│  │  - chat.py  - ingest.py  - health.py            │  │
│  └────────┬─────────────────────────────────────────┘  │
│           │                                              │
│  ┌────────▼─────────────────────────────────────────┐  │
│  │         Service Layer                            │  │
│  │  - rag_chain.py                                  │  │
│  │  - document_loader.py                            │  │
│  │  - document_monitor.py                           │  │
│  │  - web_scraper.py                                │  │
│  └────────┬─────────────────────────────────────────┘  │
│           │                                              │
│  ┌────────▼─────────────────────────────────────────┐  │
│  │         Core Layer (Singletons)                  │  │
│  │  - LLM (OpenAI GPT-4o-mini)                      │  │
│  │  - Embeddings (text-embedding-3-small)           │  │
│  │  - Vector Store (FAISS)                          │  │
│  │  - Config (Settings)                             │  │
│  └────────┬─────────────────────────────────────────┘  │
└───────────┼──────────────────────────────────────────────┘
            │
┌───────────▼──────────────────────────────────────────────┐
│              External Services                            │
│  - OpenAI API (GPT-4, Embeddings)                        │
│  - FAISS Vector Database (Local)                         │
└───────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. **FastAPI Application** (`app/main.py`)

The main entry point that:
- Initializes the FastAPI app
- Configures CORS middleware
- Mounts static files and templates
- Registers API routers
- Handles startup/shutdown events

```python
# Key responsibilities:
- Application lifecycle management
- Middleware configuration
- Route registration
- Static file serving
- Auto-processing documents on startup
```

### 2. **Configuration** (`app/core/config.py`)

Manages all application settings using Pydantic:

```python
class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str
    model_name: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    temperature: float = 0.7
    
    # Vector Store
    faiss_index_path: str = "app/data/faiss_index"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_k: int = 4
    
    # Behavior
    allow_general_knowledge: bool = True
```

**Why Pydantic?**
- Type validation
- Environment variable parsing
- Default values
- Automatic documentation

### 3. **LLM** (`app/core/llm.py`)

Initializes and manages the OpenAI language model:

```python
def get_llm():
    """
    Returns singleton LLM instance
    - Uses ChatOpenAI from LangChain
    - Configured with model name and temperature
    - Lazy initialization (created on first use)
    """
```

**Key Features:**
- Singleton pattern (one instance for entire app)
- Thread-safe initialization
- Configuration from environment
- Streaming support (future enhancement)

### 4. **Embeddings** (`app/core/embeddings.py`)

Converts text to vector representations:

```python
def get_embeddings():
    """
    Returns embedding model
    - text-embedding-3-small by default
    - Converts text to 1536-dimensional vectors
    - Used for both documents and queries
    """
```

**How Embeddings Work:**
1. Text → Tokenization → Embedding Model → Vector
2. Similar texts have similar vectors (close in vector space)
3. Enables semantic search (meaning-based, not keyword-based)

### 5. **Vector Store** (`app/core/vectorstore.py`)

FAISS database for storing and searching document vectors:

```python
class VectorStoreManager:
    def get_vectorstore():
        """Load or create FAISS index"""
    
    def save_vectorstore(vectorstore):
        """Persist index to disk"""
    
    def add_documents(documents):
        """Add new docs to existing index"""
```

**FAISS Features:**
- Fast similarity search (millions of vectors)
- Persistent storage
- Efficient memory usage
- CPU-optimized (no GPU needed)

### 6. **RAG Chain** (`app/services/rag_chain.py`)

The heart of the system - orchestrates the RAG pipeline:

```python
class RAGChain:
    def __init__(self):
        self.llm = get_llm()
        self.embeddings = get_embeddings()
        self.vectorstore = get_vectorstore()
        self.sessions = {}  # Conversation memory
    
    def answer_query(self, question, session_id):
        """
        1. Retrieve relevant documents
        2. Get conversation history
        3. Build prompt with context
        4. Generate answer with LLM
        5. Return answer + sources
        """
```

**RAG Pipeline Steps:**

```
User Question
     │
     ▼
Convert to Embedding
     │
     ▼
Search FAISS Database
     │
     ▼
Retrieve Top-K Documents
     │
     ▼
Build Prompt:
  - System instructions
  - Retrieved context
  - Conversation history
  - User question
     │
     ▼
Send to GPT-4
     │
     ▼
Get Answer
     │
     ▼
Return with Sources
```

### 7. **Document Loader** (`app/services/document_loader.py`)

Processes different file formats:

```python
class DocumentLoader:
    def load_pdf(file_path):
        """Extract text from PDF using PyPDF"""
    
    def load_docx(file_path):
        """Extract text from DOCX using python-docx"""
    
    def load_txt(file_path):
        """Read plain text files"""
    
    def chunk_documents(documents):
        """
        Split into chunks:
        - Size: 1000 characters
        - Overlap: 200 characters
        - Preserves context between chunks
        """
```

**Why Chunking?**
- LLMs have token limits
- Smaller chunks = more precise retrieval
- Overlap ensures context isn't lost at boundaries

### 8. **Document Monitor** (`app/services/document_monitor.py`)

Automatically processes new files:

```python
class DocumentMonitor:
    def process_new_documents():
        """
        1. Scan documents/ folder
        2. Find unprocessed files
        3. Load and chunk documents
        4. Add to vector store
        5. Track processed files
        """
```

**Tracking Mechanism:**
- Stores processed filenames in `app/data/.processed_files.json`
- Prevents reprocessing same files
- Runs on application startup

### 9. **Web Scraper** (`app/services/web_scraper.py`)

Extracts content from URLs:

```python
class WebScraper:
    def scrape_url(url):
        """
        1. Fetch HTML content
        2. Parse with BeautifulSoup
        3. Extract main text content
        4. Clean and format
        5. Return as document
        """
```

---

## Data Flow

### Document Ingestion Flow

```
File Upload
    │
    ▼
API Endpoint (/ingest/file)
    │
    ▼
DocumentLoader
    │
    ├─→ Load file (PDF/DOCX/TXT)
    │
    ▼
RecursiveCharacterTextSplitter
    │
    ├─→ Split into chunks (1000 chars)
    │
    ▼
OpenAI Embeddings
    │
    ├─→ Convert each chunk to vector (1536 dims)
    │
    ▼
FAISS Vector Store
    │
    ├─→ Add vectors to index
    │
    ▼
Save to Disk (app/data/faiss_index/)
    │
    ▼
Return Success Response
```

### Query Processing Flow

```
User Question
    │
    ▼
API Endpoint (/chat)
    │
    ▼
RAGChain.answer_query()
    │
    ├─→ Check session memory
    │
    ▼
OpenAI Embeddings
    │
    ├─→ Convert question to vector
    │
    ▼
FAISS Vector Store
    │
    ├─→ Similarity search (get top-K chunks)
    │
    ▼
Build Context
    │
    ├─→ Combine retrieved chunks
    ├─→ Add conversation history
    ├─→ Add system prompt
    │
    ▼
OpenAI GPT-4
    │
    ├─→ Generate answer using context
    │
    ▼
Extract Sources
    │
    ├─→ Identify which chunks were used
    │
    ▼
Update Session Memory
    │
    ▼
Return Answer + Sources
```

---

## Code Structure Explained

### `app/main.py` - Application Entry Point

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application lifecycle:
    
    Startup:
    - Log configuration
    - Auto-process new documents
    - Initialize components (lazy)
    
    Shutdown:
    - Clean up resources
    - Close connections
    """
    # Startup
    logger.info("Starting RAG Chatbot API...")
    monitor = get_document_monitor()
    result = monitor.process_new_documents()
    
    yield  # App runs here
    
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(lifespan=lifespan)
```

**Why Lifespan Events?**
- Ensures proper startup/shutdown
- Processes documents before first request
- Cleans up resources gracefully

### `app/api/chat.py` - Chat Endpoint

```python
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handles chat requests:
    1. Validate input (Pydantic)
    2. Get RAG chain instance
    3. Process query
    4. Return response
    """
    try:
        rag_chain = get_rag_chain()
        
        # Answer query with optional session memory
        result = rag_chain.answer_query(
            question=request.query,
            session_id=request.session_id,
            chat_history=request.chat_history
        )
        
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            session_id=request.session_id
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**Error Handling:**
- Catches all exceptions
- Logs errors for debugging
- Returns user-friendly HTTP errors

### `app/schemas/chat_schema.py` - Data Models

```python
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    query: str  # Required
    session_id: Optional[str] = None
    chat_history: Optional[List[ChatMessage]] = None
    
    @validator('query')
    def query_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v

class SourceDocument(BaseModel):
    content: str
    metadata: Dict[str, Any]

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
    session_id: Optional[str]
```

**Benefits of Pydantic Models:**
- Automatic validation
- Type checking
- Clear API documentation
- Serialization/deserialization

---

## Technologies Used

### Backend Stack

1. **FastAPI** (v0.110+)
   - Modern Python web framework
   - Automatic API documentation
   - Built-in validation (Pydantic)
   - Async support
   - High performance

2. **LangChain** (v0.3+)
   - RAG pipeline framework
   - LLM abstractions
   - Document loaders
   - Text splitters
   - Chain composition

3. **OpenAI API**
   - GPT-4o-mini (LLM)
   - text-embedding-3-small (Embeddings)
   - Cost-effective
   - High quality

4. **FAISS** (Facebook AI Similarity Search)
   - Vector database
   - Fast similarity search
   - CPU-optimized
   - Persistent storage

5. **Uvicorn**
   - ASGI server
   - Production-ready
   - Hot reload (development)

6. **Gunicorn** (Azure)
   - Process manager
   - Multiple workers
   - Production deployment

### Document Processing

1. **PyPDF** - PDF extraction
2. **python-docx** - Word document processing
3. **BeautifulSoup4** - Web scraping
4. **RecursiveCharacterTextSplitter** - Smart text chunking

### Frontend

1. **HTML5** - Structure
2. **CSS3** - Styling
3. **Vanilla JavaScript** - Interactivity
4. **Fetch API** - HTTP requests

---

## How RAG Works (Detailed)

### What is RAG?

**Retrieval Augmented Generation** = Retrieve relevant info + Generate answer

Traditional LLM:
```
Question → LLM → Answer (may hallucinate)
```

RAG:
```
Question → Retrieve Docs → LLM (with context) → Accurate Answer
```

### RAG Components

1. **Retrieval System**
   - Vector database (FAISS)
   - Semantic search
   - Returns relevant chunks

2. **Generation System**
   - Language model (GPT-4)
   - Uses retrieved context
   - Generates grounded answers

### Step-by-Step Example

**User asks:** "What is the company's vacation policy?"

**Step 1: Embed Query**
```python
query_embedding = embeddings.embed_query("vacation policy")
# Returns: [0.123, -0.456, 0.789, ..., 0.321]  # 1536 dimensions
```

**Step 2: Search Vector Store**
```python
relevant_docs = vectorstore.similarity_search(query_embedding, k=4)
# Returns top 4 most similar document chunks
```

**Step 3: Build Prompt**
```
System: You are a helpful assistant. Answer based only on the provided context.

Context:
[Retrieved Doc 1] Employees receive 15 vacation days per year...
[Retrieved Doc 2] Vacation must be approved by manager...
[Retrieved Doc 3] Unused vacation days expire annually...
[Retrieved Doc 4] New employees accrue 1.25 days per month...

User: What is the company's vacation policy?
```

**Step 4: Generate Answer**
```python
answer = llm.generate(prompt)
# GPT-4 generates answer using only the provided context
```

**Step 5: Return with Sources**
```json
{
  "answer": "Employees receive 15 vacation days per year...",
  "sources": [
    {"content": "Employees receive...", "metadata": {"source": "handbook.pdf", "page": 12}}
  ]
}
```

### Why RAG is Better Than Fine-Tuning

| Aspect | RAG | Fine-Tuning |
|--------|-----|-------------|
| **Update data** | Just upload new docs | Must retrain model |
| **Cost** | Low (API calls only) | High (GPU, training time) |
| **Accuracy** | High (uses exact docs) | May still hallucinate |
| **Explainable** | Shows source docs | Black box |
| **Speed** | Fast (no training) | Slow (days/weeks) |

---

## Component Details

### Conversation Memory

```python
# In RAGChain
self.sessions = {
    "user-123": ConversationBufferMemory(
        memory_key="chat_history",
        input_key="question",
        output_key="answer",
        return_messages=True
    )
}
```

**How it works:**
1. Each session ID gets its own memory
2. Stores last N message pairs
3. Included in prompt for context
4. Enables multi-turn conversations

**Example:**
```
Turn 1:
User: "What is machine learning?"
Bot: "ML is a method of data analysis..."

Turn 2:
User: "Give me an example"
Bot: (knows "example" refers to ML from Turn 1)
```

### System Prompt

```python
system_prompt = """
You are a helpful AI assistant. Your role is to answer questions 
based ONLY on the provided context documents.

Rules:
1. If the answer is in the context, provide it with confidence
2. If the answer is NOT in the context, say "I don't have enough information"
3. Do not make up or invent information
4. Cite which documents you used when possible
5. Be conversational but professional
"""
```

**Purpose:**
- Prevents hallucination
- Ensures grounded responses
- Maintains consistency
- Defines behavior boundaries

### Chunking Strategy

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # Characters per chunk
    chunk_overlap=200,      # Overlap between chunks
    separators=["\n\n", "\n", ".", " ", ""]  # Split hierarchy
)
```

**Why this approach?**
- **1000 chars**: Balance between context and precision
- **200 overlap**: Prevents context loss at boundaries
- **Hierarchical splitting**: Respects document structure

**Example:**
```
Original Text (2500 chars):
"Paragraph 1... Paragraph 2... Paragraph 3..."

After Chunking:
Chunk 1 (0-1000): "Paragraph 1... Paragraph 2..."
Chunk 2 (800-1800): "...graph 2... Paragraph 3..." [overlap from 800-1000]
Chunk 3 (1600-2500): "...graph 3..." [overlap from 1600-1800]
```

### Similarity Search Algorithm

```python
# FAISS uses cosine similarity
similarity = cosine(query_vector, document_vector)
# Returns score 0-1 (1 = identical, 0 = completely different)

# Top-K selection
top_docs = sorted(all_docs, key=lambda d: similarity(query, d))[:k]
```

**How FAISS is Fast:**
- Uses approximation algorithms (IVF, PQ)
- Indexes vectors for quick lookup
- Parallel processing
- Optimized C++ code

### Token Management

```python
# Ensure prompt doesn't exceed token limits
max_tokens = 4096  # GPT-4o-mini limit

# Calculate tokens
prompt_tokens = count_tokens(system_prompt + context + question)

if prompt_tokens > max_tokens:
    # Truncate context or use fewer chunks
    context = context[:max_context_length]
```

**Token Limits:**
- GPT-4o-mini: 128K input, 16K output
- text-embedding-3-small: 8191 input

---

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading**
   ```python
   # Don't load LLM until first use
   _llm = None
   def get_llm():
       global _llm
       if _llm is None:
           _llm = ChatOpenAI(...)
       return _llm
   ```

2. **Caching**
   - FAISS index loaded once
   - Embeddings model reused
   - Session memory in-memory

3. **Async Operations**
   ```python
   @router.post("/chat")
   async def chat(request: ChatRequest):
       # Can handle multiple requests concurrently
   ```

4. **Worker Processes**
   ```bash
   gunicorn --workers 4 app.main:app
   # Multiple processes for parallel handling
   ```

### Scaling Considerations

**Vertical Scaling (Single Machine):**
- Increase workers: `--workers 8`
- More RAM for larger vector stores
- Faster CPU for embeddings

**Horizontal Scaling (Multiple Machines):**
- Load balancer in front
- Shared FAISS index (network storage)
- Redis for session storage
- Rate limiting per API key

---

## Security Considerations

1. **API Key Protection**
   - Never commit `.env`
   - Use environment variables
   - Rotate keys regularly

2. **Input Validation**
   - Pydantic models validate all inputs
   - File type checking
   - Size limits on uploads

3. **CORS**
   ```python
   # Production: Restrict origins
   CORS_ORIGINS=["https://trusted-site.com"]
   ```

4. **Rate Limiting** (TODO)
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   @limiter.limit("10/minute")
   async def chat(...):
   ```

---

## Monitoring & Debugging

### Logging

```python
# app/utils/logger.py
logger.info("Normal operation")
logger.warning("Something unusual")
logger.error("Error occurred", exc_info=True)
```

**Log locations:**
- Console (stdout)
- File: `logs/rag_chatbot_YYYYMMDD.log`

### Health Checks

```python
@router.get("/health")
async def health():
    return {
        "status": "healthy",
        "documents_indexed": vectorstore.index.ntotal,
        "model": settings.model_name
    }
```

**Use for:**
- Load balancer health checks
- Monitoring systems
- Deployment verification

### Debugging Tips

1. **Check logs first:**
   ```bash
   tail -f logs/rag_chatbot_*.log
   ```

2. **Test endpoints with /docs:**
   - Interactive API testing
   - See request/response formats

3. **Verify environment:**
   ```python
   # Check settings are loaded
   from app.core.config import get_settings
   print(get_settings())
   ```

4. **Inspect vector store:**
   ```python
   vectorstore = get_vectorstore()
   print(f"Documents: {vectorstore.index.ntotal}")
   ```

---

## Future Enhancements

Potential improvements:

1. **Streaming Responses**
   - Stream tokens as generated
   - Better UX for long answers

2. **Document Metadata Filtering**
   - Filter by date, author, category
   - More precise retrieval

3. **Multi-modal Support**
   - Images, tables, charts
   - Vision models

4. **Advanced RAG**
   - Re-ranking retrieved docs
   - Hybrid search (keyword + semantic)
   - Query decomposition

5. **Authentication**
   - User accounts
   - API keys
   - Usage tracking

6. **Analytics**
   - Query patterns
   - Popular questions
   - Response quality metrics

---

## Conclusion

This RAG Chatbot demonstrates:
- **Clean architecture** with separation of concerns
- **Production-ready** code with error handling and logging
- **Scalable design** using industry-standard tools
- **Well-documented** with clear examples

The modular design makes it easy to:
- Swap LLM providers
- Change vector databases
- Add new document types
- Extend functionality

---

**Questions?** Check [README.md](README.md) or [API_GUIDE.md](API_GUIDE.md)
