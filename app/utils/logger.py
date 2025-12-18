"""
Logging Configuration
Centralized logging setup for the application
"""
import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logger(name: str = "rag_chatbot", level: int = logging.INFO) -> logging.Logger:
    """
    Setup and configure application logger
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    simple_formatter = logging.Formatter(
        fmt="%(levelname)s - %(message)s"
    )
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler (detailed logs)
    try:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"rag_chatbot_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create file handler: {e}")
    
    return logger


# Global logger instance
logger = setup_logger()


def get_logger(name: str = None) -> logging.Logger:
    """
    Get logger instance
    
    Args:
        name: Optional logger name
        
    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"rag_chatbot.{name}")
    return logger
