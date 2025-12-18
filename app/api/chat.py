"""
Chat Endpoint
Handles user queries and returns AI responses using RAG
"""
from fastapi import APIRouter, HTTPException
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.rag_chain import get_rag_chain
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - Answer user questions using RAG
    
    Args:
        request: ChatRequest with query, optional session_id and chat_history
        
    Returns:
        ChatResponse with answer and source documents
    """
    try:
        logger.info(f"Received chat request: {request.query[:100]}...")
        
        rag_chain = get_rag_chain()
        
        # If session_id provided and no chat_history, use persistent memory
        if request.session_id and not request.chat_history:
            answer, sources = rag_chain.query_with_memory(
                question=request.query,
                session_id=request.session_id
            )
        else:
            # Use provided chat history
            answer, sources = rag_chain.query(
                question=request.query,
                session_id=request.session_id,
                chat_history=request.chat_history
            )
        
        response = ChatResponse(
            answer=answer,
            sources=sources,
            session_id=request.session_id
        )
        
        logger.info(f"Chat response generated successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )
