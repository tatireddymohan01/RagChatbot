"""
Web Scraper Service
Handles scraping and processing web content using Playwright (JS-capable) with requests fallback
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
import requests
from app.utils.logger import get_logger

# Playwright imports
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    async_playwright = None

logger = get_logger(__name__)


class WebScraperService:
    """Service for scraping web content (Selenium + HTTP fallback)"""
    
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

    def scrape_multiple_urls_simple(self, urls: List[str]) -> List[Document]:
        """
        Scrape URLs using Playwright (handles JS rendering) with fallback to requests.
        Cloud-safe, no ChromeDriver dependency.
        """
        results: List[Document] = []
        failed: List[str] = []
        
        logger.info(f"[SCRAPE_START] Processing {len(urls)} URLs with Playwright")

        for url in urls:
            try:
                logger.info(f"[SCRAPE_FETCH] Starting: {url}")
                
                # Try Playwright first (handles JavaScript)
                doc = self._scrape_with_playwright(url)
                if doc and len(doc.page_content) > 100:
                    logger.info(f"[SCRAPE_SUCCESS] ✓ Playwright: {len(doc.page_content)} chars")
                    results.append(doc)
                    continue
                
                # Fallback to requests + BeautifulSoup for simple pages
                logger.info(f"[SCRAPE_FETCH] Playwright failed/empty, trying requests fallback...")
                doc = self._scrape_with_requests(url)
                if doc and len(doc.page_content) > 100:
                    logger.info(f"[SCRAPE_SUCCESS] ✓ Requests: {len(doc.page_content)} chars")
                    results.append(doc)
                else:
                    failed.append(url)
                    logger.warning(f"[SCRAPE_FAIL] ✗ Both methods failed for {url}")
                    
            except Exception as exc:
                failed.append(url)
                logger.error(f"[SCRAPE_ERROR] Exception for {url}: {type(exc).__name__}: {str(exc)[:120]}")

        logger.info(f"[SCRAPE_END] Summary: {len(results)} succeeded, {len(failed)} failed out of {len(urls)} total")
        if failed:
            logger.warning(f"[SCRAPE_END] Failed URLs: {failed[:10]}")

        return results
    
    def _scrape_with_playwright(self, url: str) -> Document:
        """Scrape URL using Playwright (handles JavaScript rendering)"""
        try:
            if not PLAYWRIGHT_AVAILABLE:
                logger.info(f"[PLAYWRIGHT] Not available, skipping")
                return None
            
            import asyncio
            
            # Run async playwright in sync context
            async def scrape():
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    try:
                        page = await browser.new_page(
                            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                        )
                        logger.info(f"[PLAYWRIGHT] Navigating to {url}")
                        await page.goto(url, timeout=15000, wait_until="networkidle")
                        
                        # Get rendered HTML after JavaScript execution
                        html_content = await page.content()
                        logger.info(f"[PLAYWRIGHT] Rendered HTML size: {len(html_content)} chars")
                        
                        return html_content
                    finally:
                        await browser.close()
            
            # Get or create event loop
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            html_content = loop.run_until_complete(scrape())
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Remove noise
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
                tag.decompose()
            
            # Extract main content
            main_content = None
            for selector in ["main", "article", "[role='main']", ".content", ".main-content", ".container"]:
                elem = soup.select_one(selector)
                if elem:
                    main_content = elem
                    break
            
            content_elem = main_content if main_content else soup.body or soup
            text = content_elem.get_text(separator="\n", strip=True)
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            cleaned = "\n".join(lines)
            
            title = soup.title.string if soup.title else urlparse(url).path or url
            
            if cleaned and len(cleaned) > 100:
                logger.info(f"[PLAYWRIGHT] ✓ Extracted {len(cleaned)} chars")
                return Document(
                    page_content=cleaned,
                    metadata={
                        "source": url,
                        "title": title,
                        "type": "web_page",
                        "domain": urlparse(url).netloc,
                        "scraper": "playwright"
                    },
                )
            else:
                logger.info(f"[PLAYWRIGHT] Content too small ({len(cleaned)} chars)")
                return None
                
        except Exception as e:
            logger.warning(f"[PLAYWRIGHT] Error: {type(e).__name__}: {str(e)[:100]}")
            return None
    
    def _scrape_with_requests(self, url: str) -> Document:
        """Scrape URL using requests + BeautifulSoup (fallback for simple pages)"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            logger.info(f"[REQUESTS] Fetching {url}")
            resp = requests.get(url, timeout=15, headers=headers)
            resp.raise_for_status()
            logger.info(f"[REQUESTS] Status 200 OK, HTML size: {len(resp.text)} chars")

            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Remove noise
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
                tag.decompose()

            # Try main content extraction
            main_content = None
            for selector in ["main", "article", "[role='main']", ".content", ".main-content", ".container"]:
                elem = soup.select_one(selector)
                if elem:
                    main_content = elem
                    break
            
            content_elem = main_content if main_content else soup.body or soup
            text = content_elem.get_text(separator="\n", strip=True)
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            cleaned = "\n".join(lines)
            
            title = soup.title.string if soup.title else urlparse(url).path or url
            
            # Try meta tag fallback if content is small
            if not cleaned or len(cleaned) < 100:
                logger.info(f"[REQUESTS] Main content too small, trying meta tags...")
                meta_description = soup.find("meta", attrs={"name": "description"})
                og_description = soup.find("meta", attrs={"property": "og:description"})
                og_title = soup.find("meta", attrs={"property": "og:title"})
                
                fallback_parts = []
                if og_title:
                    fallback_parts.append(og_title.get("content", ""))
                if meta_description:
                    fallback_parts.append(meta_description.get("content", ""))
                if og_description:
                    fallback_parts.append(og_description.get("content", ""))
                
                cleaned = "\n".join([p for p in fallback_parts if p])
                logger.info(f"[REQUESTS] Meta extraction: {len(cleaned)} chars")
            
            if cleaned and len(cleaned) > 50:
                logger.info(f"[REQUESTS] ✓ Extracted {len(cleaned)} chars")
                return Document(
                    page_content=cleaned,
                    metadata={
                        "source": url,
                        "title": title,
                        "type": "web_page",
                        "domain": urlparse(url).netloc,
                        "scraper": "requests"
                    },
                )
            else:
                logger.info(f"[REQUESTS] Content too small ({len(cleaned)} chars)")
                return None
                
        except Exception as e:
            logger.warning(f"[REQUESTS] Error: {type(e).__name__}: {str(e)[:100]}")
            return None
    
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
