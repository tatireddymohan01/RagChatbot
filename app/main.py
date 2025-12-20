"""
FastAPI Main Application
Production-grade RAG Chatbot Backend
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional
from app.api import chat, ingest, health
from app.core.config import get_settings
from app.services.document_monitor import get_document_monitor
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting RAG Chatbot API...")
    settings = get_settings()
    logger.info(f"Application: {settings.app_name} v{settings.app_version}")
    
    # Log which models are being used
    if settings.use_huggingface_llm:
        logger.info(f"LLM: {settings.huggingface_llm_model} (Hugging Face)")
    else:
        logger.info(f"LLM: {settings.model_name} (OpenAI)")
    
    if settings.use_huggingface_embeddings:
        logger.info(f"Embeddings: {settings.huggingface_model_name} (Hugging Face)")
    else:
        logger.info(f"Embeddings: {settings.embedding_model} (OpenAI)")
    
    logger.info(f"HF Cache Dir: {settings.huggingface_cache_dir}")
    logger.info(f"FAISS Index Path: {settings.faiss_index_path}")
    logger.info(f"Documents Folder: {settings.documents_folder}")
    
    # Auto-process new documents from folder
    try:
        logger.info("Checking for new documents in folder...")
        monitor = get_document_monitor()
        result = monitor.process_new_documents()
        if result['documents_processed'] > 0:
            logger.info(f"✅ Auto-processed {result['documents_processed']} document(s) on startup")
        else:
            logger.info("No new documents to process")
    except Exception as e:
        logger.error(f"Error during auto-processing: {e}")
    
    # Initialize components (lazy loading will happen on first use)
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down RAG Chatbot API...")


# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="Production-grade chatbot backend using FastAPI + LangChain RAG",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Mount static files and templates only if not in API-only mode
templates: Optional[Jinja2Templates] = None
if not settings.api_only:
    app.mount("/static", StaticFiles(directory="ui/static"), name="static")
    templates = Jinja2Templates(directory="ui/templates")
    logger.info("UI serving enabled")
else:
    logger.info("Running in API-only mode (UI disabled)")

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(chat.router, tags=["Chat"])
app.include_router(ingest.router, tags=["Ingestion"])


@app.get("/")
async def root(request: Request):
    """Root endpoint - Serve the chat UI or API info"""
    if settings.api_only or templates is None:
        return {
            "message": "RAG Chatbot API",
            "version": "1.0.0",
            "mode": "API-only",
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "endpoints": {
                "chat": "POST /chat",
                "ingest_text": "POST /ingest/text",
                "ingest_file": "POST /ingest/file",
                "ingest_url": "POST /ingest/url"
            }
        }
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "message": "RAG Chatbot API",
        "version": "1.0.0",
        "mode": "API-only" if settings.api_only else "Full (API + UI)",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "ui": "/" if not settings.api_only else None
    }


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
