"""
Ingestion API Schemas
Request and response models for document/URL ingestion
"""
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, model_validator


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


class URLDeleteRequest(BaseModel):
    """URL deletion request"""
    url: Optional[HttpUrl] = Field(default=None, description="Specific URL to delete from the index")
    domain: Optional[str] = Field(default=None, description="Domain to delete all scraped pages")

    @model_validator(mode="before")
    def at_least_one(cls, values):
        if not values.get("url") and not values.get("domain"):
            raise ValueError("Either url or domain must be provided")
        return values
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/article",
                "domain": None
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
