"""
Configuration Management
Handles all environment variables and application settings using Pydantic BaseSettings
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    app_name: str = "RAG Chatbot API"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, description="Debug mode")
    
    # OpenAI Configuration (Optional when using Hugging Face)
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    model_name: str = Field(default="gpt-4o-mini", description="OpenAI model name")
    temperature: float = Field(default=0.0, description="LLM temperature")
    
    # Embeddings Configuration
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model"
    )
    # Alternative: Use HuggingFace embeddings if OpenAI not available
    use_huggingface_embeddings: bool = Field(
        default=False,
        description="Use HuggingFace embeddings instead of OpenAI"
    )
    huggingface_model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="HuggingFace embedding model"
    )
    
    # Hugging Face LLM Configuration
    use_huggingface_llm: bool = Field(
        default=False,
        description="Use HuggingFace LLM instead of OpenAI"
    )
    huggingface_llm_model: str = Field(
        default="mistralai/Mistral-7B-Instruct-v0.1",
        description="HuggingFace LLM model"
    )
    huggingface_api_token: Optional[str] = Field(
        default=None,
        description="Hugging Face API token (for private models)"
    )
    huggingface_cache_dir: str = Field(
        default="D:/HuggingFace/cache",
        description="Hugging Face cache directory path"
    )
    
    # Vector Store Configuration
    faiss_index_path: str = Field(
        default="app/data/faiss_index",
        description="Path to FAISS index storage"
    )
    chunk_size: int = Field(default=1000, description="Text chunk size")
    chunk_overlap: int = Field(default=200, description="Text chunk overlap")
    
    # RAG Configuration
    retrieval_k: int = Field(default=4, description="Number of documents to retrieve")
    allow_general_knowledge: bool = Field(
        default=True,
        description="Allow AI to use general knowledge when documents don't contain the answer"
    )
    
    # CORS Configuration
    cors_origins: list = Field(
        default=["*"],
        description="Allowed CORS origins"
    )
    
    # API Mode Configuration
    api_only: bool = Field(
        default=False,
        description="Run in API-only mode (no UI serving)"
    )
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # Azure Deployment Configuration (for production)
    azure_deployment: bool = Field(default=False, description="Running on Azure")
    azure_storage_connection_string: Optional[str] = Field(
        default=None,
        description="Azure Storage connection string for persistent storage"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance"""
    return settings
