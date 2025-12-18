"""
Embeddings Configuration
Manages OpenAI and HuggingFace embeddings initialization
"""
from typing import Union
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_embeddings() -> Union[OpenAIEmbeddings, HuggingFaceEmbeddings]:
    """
    Initialize and return embeddings model
    Tries OpenAI first, falls back to HuggingFace if configured
    
    Returns:
        Embeddings instance (OpenAI or HuggingFace)
    """
    settings = get_settings()
    
    try:
        if settings.use_huggingface_embeddings:
            logger.info(f"Initializing HuggingFace embeddings: {settings.huggingface_model_name}")
            embeddings = HuggingFaceEmbeddings(
                model_name=settings.huggingface_model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            logger.info("HuggingFace embeddings initialized successfully")
            return embeddings
        else:
            logger.info(f"Initializing OpenAI embeddings: {settings.embedding_model}")
            embeddings = OpenAIEmbeddings(
                model=settings.embedding_model,
                openai_api_key=settings.openai_api_key
            )
            logger.info("OpenAI embeddings initialized successfully")
            return embeddings
            
    except Exception as e:
        logger.error(f"Failed to initialize embeddings: {e}")
        
        # Fallback to HuggingFace if OpenAI fails
        if not settings.use_huggingface_embeddings:
            logger.warning("Falling back to HuggingFace embeddings")
            try:
                embeddings = HuggingFaceEmbeddings(
                    model_name=settings.huggingface_model_name,
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
                logger.info("HuggingFace embeddings (fallback) initialized successfully")
                return embeddings
            except Exception as fallback_error:
                logger.error(f"Fallback embeddings also failed: {fallback_error}")
                raise
        else:
            raise
