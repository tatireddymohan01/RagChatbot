"""
Web Scraper Service
Handles scraping and processing web content using Selenium
"""
from typing import List
from langchain_core.documents import Document
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import time
from app.utils.logger import get_logger

logger = get_logger(__name__)


class WebScraperService:
    """Service for scraping web content using Selenium"""
    
    def __init__(self):
        pass
    
    def discover_urls(self, base_url: str) -> set:
        """
        Discover all internal URLs from a base URL using Selenium
        
        Args:
            base_url: Base URL to crawl
            
        Returns:
            Set of discovered URLs
        """
        try:
            logger.info(f"Discovering URLs from: {base_url}")
            
            # Setup Selenium with headless mode
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(base_url)
            time.sleep(3)  # Wait for page to load
            
            # Extract all links
            base_netloc = urlparse(base_url).netloc
            urls = set([base_url])
            
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                try:
                    href = link.get_attribute("href")
                    if href and urlparse(href).netloc == base_netloc:
                        # Clean URL: remove fragments, exclude special protocols
                        if not any(href.startswith(p) for p in ['#', 'mailto:', 'tel:', 'javascript:']):
                            urls.add(href.split('#')[0])
                except:
                    continue
            
            driver.quit()
            
            logger.info(f"Found {len(urls)} unique URLs")
            return urls
            
        except Exception as e:
            logger.error(f"Error discovering URLs: {e}")
            raise
    
    def scrape_multiple_urls_selenium(self, urls: List[str]) -> List[Document]:
        """
        Scrape multiple URLs using direct Selenium (no SeleniumURLLoader dependency)
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of Document objects
        """
        try:
            logger.info(f"Starting to scrape {len(urls)} URLs with Selenium")
            
            all_data = []
            failed_urls = []
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                for url in urls:
                    try:
                        logger.info(f"Scraping: {url}")
                        driver.get(url)
                        
                        # Wait for body to load
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )
                        time.sleep(2)  # Extra wait for dynamic content
                        
                        # Get page source and parse with BeautifulSoup
                        page_source = driver.page_source
                        soup = BeautifulSoup(page_source, 'html.parser')
                        
                        # Remove script, style, and other non-content elements
                        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                            element.decompose()
                        
                        # Extract text
                        text = soup.get_text(separator="\n", strip=True)
                        lines = [line.strip() for line in text.splitlines() if line.strip()]
                        cleaned_text = "\n".join(lines)
                        
                        # Get title
                        title = soup.title.string if soup.title else urlparse(url).path
                        
                        # Create document
                        doc = Document(
                            page_content=cleaned_text,
                            metadata={
                                "source": url,
                                "title": title,
                                "type": "web_page",
                                "domain": urlparse(url).netloc
                            }
                        )
                        
                        all_data.append(doc)
                        logger.info(f"✓ Successfully scraped: {url}")
                        
                    except Exception as e:
                        failed_urls.append(url)
                        logger.warning(f"✗ Failed to scrape {url}: {str(e)[:100]}")
                
            finally:
                driver.quit()
            
            logger.info(f"\n=== Scraping Summary ===")
            logger.info(f"Success: {len(all_data)} | Failed: {len(failed_urls)}")
            
            if failed_urls:
                logger.warning(f"Failed URLs: {failed_urls}")
            
            return all_data
                
        except Exception as e:
            logger.error(f"Error scraping multiple URLs with Selenium: {e}")
            raise
    
    def scrape_website(self, base_url: str) -> List[Document]:
        """
        Scrape entire website: discover all URLs and scrape them
        
        Args:
            base_url: Base URL of the website
            
        Returns:
            List of Document objects from all pages
        """
        try:
            logger.info(f"Starting full website scrape: {base_url}")
            
            # Step 1: Discover all URLs
            urls = self.discover_urls(base_url)
            
            # Step 2: Scrape all discovered URLs
            documents = self.scrape_multiple_urls_selenium(list(urls))
            
            logger.info(f"Successfully scraped {len(documents)} pages from website")
            return documents
            
        except Exception as e:
            logger.error(f"Error scraping website: {e}")
            raise


# Global scraper instance
_web_scraper: WebScraperService = None


def get_web_scraper() -> WebScraperService:
    """Get or create the global WebScraperService instance"""
    global _web_scraper
    
    if _web_scraper is None:
        _web_scraper = WebScraperService()
    
    return _web_scraper
