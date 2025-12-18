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
from app.api import chat, ingest, health
from app.core.config import get_settings
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
    logger.info(f"Model: {settings.model_name}")
    logger.info(f"FAISS Index Path: {settings.faiss_index_path}")
    
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
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(chat.router, tags=["Chat"])
app.include_router(ingest.router, tags=["Ingestion"])


@app.get("/")
async def root(request: Request):
    """Root endpoint - Serve the chat UI"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "message": "RAG Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "ui": "/"
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
