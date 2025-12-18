"""
Chat API Schemas
Request and response models for chat endpoints
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat request payload"""
    query: str = Field(..., description="User query", min_length=1)
    session_id: Optional[str] = Field(
        default=None,
        description="Session ID for conversation history"
    )
    chat_history: Optional[List[ChatMessage]] = Field(
        default=[],
        description="Previous chat messages in the conversation"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is machine learning?",
                "session_id": "user-123",
                "chat_history": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi! How can I help you?"}
                ]
            }
        }


class SourceDocument(BaseModel):
    """Source document metadata"""
    content: str = Field(..., description="Document content snippet")
    source: str = Field(..., description="Document source")
    page: Optional[int] = Field(default=None, description="Page number if applicable")


class ChatResponse(BaseModel):
    """Chat response payload"""
    answer: str = Field(..., description="Chatbot answer")
    sources: List[SourceDocument] = Field(
        default=[],
        description="Source documents used to generate the answer"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Session ID for the conversation"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Machine learning is a subset of artificial intelligence...",
                "sources": [
                    {
                        "content": "Machine learning is a method of data analysis...",
                        "source": "ml_intro.pdf",
                        "page": 1
                    }
                ],
                "session_id": "user-123"
            }
        }
