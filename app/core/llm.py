"""
LLM Configuration and Initialization
Manages ChatOpenAI instance with proper configuration
"""
from langchain_openai import ChatOpenAI
from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_llm() -> ChatOpenAI:
    """
    Initialize and return ChatOpenAI LLM instance
    
    Returns:
        Configured ChatOpenAI instance
    """
    settings = get_settings()
    
    try:
        llm = ChatOpenAI(
            model=settings.model_name,
            temperature=settings.temperature,
            openai_api_key=settings.openai_api_key,
            max_tokens=None,  # Let model use default
            request_timeout=60,
        )
        
        logger.info(f"LLM initialized: {settings.model_name} with temperature {settings.temperature}")
        return llm
        
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        raise


def get_chat_llm_with_system_prompt(system_prompt: str = None) -> ChatOpenAI:
    """
    Get LLM with a custom system prompt configuration
    
    Args:
        system_prompt: Custom system prompt (optional)
        
    Returns:
        Configured ChatOpenAI instance
    """
    llm = get_llm()
    
    if system_prompt:
        logger.info("Using custom system prompt")
    
    return llm


# Default system prompt for RAG
DEFAULT_SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions based ONLY on the provided context.

IMPORTANT RULES:
1. Answer questions using ONLY the information from the retrieved context/documents
2. If the answer is not in the context, you MUST respond with "I don't know" or "I don't have enough information to answer that question"
3. Do NOT make up information or use external knowledge
4. Be concise and accurate
5. If you cite information, mention which source document it came from
6. Maintain a professional and helpful tone

Context will be provided to you along with the user's question."""
