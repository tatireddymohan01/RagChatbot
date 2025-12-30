"""
Ingestion API Schemas
Request and response models for document/URL ingestion
"""
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class URLIngestRequest(BaseModel):
    """URL ingestion request"""
    url: HttpUrl = Field(..., description="URL to scrape and ingest")
    scrape_full_site: bool = Field(default=False, description="Whether to scrape the entire website or just the single URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
                "scrape_full_site": False
            }
        }


class IngestResponse(BaseModel):
    """Ingestion response"""
    status: str = Field(..., description="Ingestion status")
    message: str = Field(..., description="Status message")
    documents_processed: int = Field(
        default=0,
        description="Number of documents processed"
    )
    chunks_created: int = Field(
        default=0,
        description="Number of text chunks created"
    )
    sources: Optional[List[str]] = Field(
        default=[],
        description="List of ingested sources"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Documents ingested successfully",
                "documents_processed": 3,
                "chunks_created": 45,
                "sources": ["document1.pdf", "document2.docx", "document3.txt"]
            }
        }
