"""
Web Scraper Service
Handles scraping and processing web content
"""
from typing import List
import requests
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from langchain_community.document_loaders import WebBaseLoader
from app.utils.logger import get_logger

logger = get_logger(__name__)


class WebScraperService:
    """Service for scraping web content"""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def scrape_url_langchain(self, url: str) -> List[Document]:
        """
        Scrape URL using LangChain WebBaseLoader
        
        Args:
            url: URL to scrape
            
        Returns:
            List of Document objects
        """
        try:
            logger.info(f"Scraping URL with LangChain: {url}")
            
            loader = WebBaseLoader(
                web_paths=[url],
                header_template=self.headers
            )
            
            documents = loader.load()
            
            # Add metadata
            for doc in documents:
                doc.metadata["source"] = url
                doc.metadata["type"] = "web_page"
            
            logger.info(f"Successfully scraped {len(documents)} document(s) from {url}")
            return documents
            
        except Exception as e:
            logger.error(f"Error scraping URL with LangChain: {e}")
            raise
    
    def scrape_url_beautifulsoup(self, url: str) -> List[Document]:
        """
        Scrape URL using BeautifulSoup (fallback method)
        
        Args:
            url: URL to scrape
            
        Returns:
            List of Document objects
        """
        try:
            logger.info(f"Scraping URL with BeautifulSoup: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text(separator="\n", strip=True)
            
            # Clean up text
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            cleaned_text = "\n".join(lines)
            
            # Get page title
            title = soup.title.string if soup.title else "Untitled"
            
            # Create document
            document = Document(
                page_content=cleaned_text,
                metadata={
                    "source": url,
                    "title": title,
                    "type": "web_page"
                }
            )
            
            logger.info(f"Successfully scraped content from {url}")
            return [document]
            
        except Exception as e:
            logger.error(f"Error scraping URL with BeautifulSoup: {e}")
            raise
    
    def scrape_url(self, url: str, use_fallback: bool = True) -> List[Document]:
        """
        Scrape URL with automatic fallback
        
        Args:
            url: URL to scrape
            use_fallback: Whether to use BeautifulSoup fallback if LangChain fails
            
        Returns:
            List of Document objects
        """
        try:
            # Try LangChain first
            return self.scrape_url_langchain(url)
            
        except Exception as e:
            logger.warning(f"LangChain scraping failed: {e}")
            
            if use_fallback:
                logger.info("Attempting fallback with BeautifulSoup")
                try:
                    return self.scrape_url_beautifulsoup(url)
                except Exception as fallback_error:
                    logger.error(f"Fallback scraping also failed: {fallback_error}")
                    raise
            else:
                raise
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if URL is accessible
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is accessible, False otherwise
        """
        try:
            response = requests.head(url, headers=self.headers, timeout=10, allow_redirects=True)
            return response.status_code < 400
        except Exception as e:
            logger.warning(f"URL validation failed for {url}: {e}")
            return False


# Global scraper instance
_web_scraper: WebScraperService = None


def get_web_scraper() -> WebScraperService:
    """Get or create the global WebScraperService instance"""
    global _web_scraper
    
    if _web_scraper is None:
        _web_scraper = WebScraperService()
    
    return _web_scraper
