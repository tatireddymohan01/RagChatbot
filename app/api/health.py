"""
Health Check Endpoint
"""
from fastapi import APIRouter
from datetime import datetime
from app.core.config import get_settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    Returns API status and basic information
    """
    settings = get_settings()
    
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
        "model": settings.model_name
    }
