"""
LLM Configuration and Initialization
Manages OpenAI and Hugging Face LLM instances with proper configuration
"""
from typing import Union
from langchain_openai import ChatOpenAI
from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_llm() -> Union[ChatOpenAI, any]:
    """
    Initialize and return LLM instance (OpenAI or Hugging Face)
    
    Returns:
        Configured LLM instance
    """
    settings = get_settings()
    
    try:
        # Use Hugging Face if configured
        if settings.use_huggingface_llm:
            logger.info(f"Initializing Hugging Face LLM: {settings.huggingface_llm_model}")
            
            try:
                from langchain_community.llms import HuggingFacePipeline
                from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
                import torch
                
                # Check if GPU is available
                device = "cuda" if torch.cuda.is_available() else "cpu"
                logger.info(f"Using device: {device}")
                
                # Load model and tokenizer
                tokenizer = AutoTokenizer.from_pretrained(
                    settings.huggingface_llm_model,
                    cache_dir=settings.huggingface_cache_dir
                )
                model = AutoModelForCausalLM.from_pretrained(
                    settings.huggingface_llm_model,
                    cache_dir=settings.huggingface_cache_dir,
                    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                    device_map="auto" if device == "cuda" else None,
                    low_cpu_mem_usage=True
                )
                
                # Create pipeline
                pipe = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    max_new_tokens=512,
                    temperature=settings.temperature,
                    do_sample=True if settings.temperature > 0 else False,
                    top_p=0.95,
                )
                
                llm = HuggingFacePipeline(pipeline=pipe)
                logger.info(f"Hugging Face LLM initialized successfully on {device}")
                return llm
                
            except ImportError as ie:
                logger.error(f"Hugging Face dependencies not installed: {ie}")
                logger.info("Run: pip install transformers torch huggingface-hub accelerate")
                raise
            except Exception as hf_error:
                logger.error(f"Failed to initialize Hugging Face LLM: {hf_error}")
                raise
        
        # Use OpenAI (default)
        else:
            llm = ChatOpenAI(
                model=settings.model_name,
                temperature=settings.temperature,
                openai_api_key=settings.openai_api_key,
                max_tokens=None,
                request_timeout=60,
            )
            
            logger.info(f"OpenAI LLM initialized: {settings.model_name} with temperature {settings.temperature}")
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


# Default system prompt for RAG with fallback to general knowledge
def get_system_prompt(allow_general_knowledge: bool = True) -> str:
    """
    Get the system prompt based on configuration
    
    Args:
        allow_general_knowledge: Whether to allow AI to use general knowledge
        
    Returns:
        Appropriate system prompt
    """
    if allow_general_knowledge:
        return """You are a helpful AI assistant that provides accurate and informative answers.

ANSWER PRIORITY:
1. PRIMARY: If the provided context/documents contain relevant information, use that information to answer the question and cite the source
2. FALLBACK: If the context doesn't contain the answer, use your general knowledge to provide a helpful response
3. When using context, mention: "Based on the provided documents..."
4. When using general knowledge, mention: "Based on my knowledge..." or "Generally speaking..."

IMPORTANT RULES:
- Prioritize document context when available
- Be transparent about your information source (documents vs general knowledge)
- Be concise and accurate
- Maintain a professional and helpful tone
- If you truly don't know something, say so

Context from documents will be provided below (may be empty if no relevant documents found)."""
    else:
        return """You are a helpful AI assistant that answers questions based ONLY on the provided context.

IMPORTANT RULES:
1. Answer questions using ONLY the information from the retrieved context/documents
2. If the answer is not in the context, you MUST respond with "I don't know" or "I don't have enough information to answer that question"
3. Do NOT make up information or use external knowledge
4. Be concise and accurate
5. If you cite information, mention which source document it came from
6. Maintain a professional and helpful tone

Context will be provided to you along with the user's question."""


# Keep backward compatibility
DEFAULT_SYSTEM_PROMPT = get_system_prompt(True)
