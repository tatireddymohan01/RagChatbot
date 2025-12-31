"""
Sitemap Crawler Service
Parses sitemap.xml and extracts all URLs for batch ingestion
"""
from typing import List, Set
from urllib.parse import urljoin, urlparse
import requests
from xml.etree import ElementTree as ET
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SitemapCrawlerService:
    """Service for parsing sitemaps and extracting URLs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 10
    
    def _get_sitemap_url(self, domain: str) -> str:
        """Construct sitemap URL from domain"""
        # Ensure domain has scheme
        if not domain.startswith(('http://', 'https://')):
            domain = 'https://' + domain
        
        # Remove trailing slash
        domain = domain.rstrip('/')
        
        return f"{domain}/sitemap.xml"
    
    def parse_sitemap(self, sitemap_url: str) -> List[str]:
        """
        Parse sitemap.xml and extract all URLs
        Handles both regular sitemaps and sitemap indexes
        
        Args:
            sitemap_url: URL to sitemap.xml or domain
            
        Returns:
            List of extracted URLs
        """
        try:
            # If domain provided, construct sitemap URL
            if not sitemap_url.endswith('sitemap.xml'):
                sitemap_url = self._get_sitemap_url(sitemap_url)
            
            logger.info(f"Fetching sitemap: {sitemap_url}")
            
            response = self.session.get(sitemap_url, timeout=15)
            response.raise_for_status()
            
            urls = self._extract_urls_from_xml(response.text, sitemap_url)
            
            logger.info(f"Found {len(urls)} URLs in sitemap")
            return list(urls)
            
        except requests.RequestException as e:
            logger.error(f"Error fetching sitemap: {e}")
            raise Exception(f"Failed to fetch sitemap: {str(e)}")
        except ET.ParseError as e:
            logger.error(f"Error parsing sitemap XML: {e}")
            raise Exception(f"Invalid sitemap XML: {str(e)}")
    
    def _extract_urls_from_xml(self, xml_content: str, base_url: str) -> Set[str]:
        """
        Extract URLs from sitemap XML
        Handles both urlset and sitemapindex
        
        Args:
            xml_content: XML content as string
            base_url: Base URL for relative links
            
        Returns:
            Set of unique URLs
        """
        urls = set()
        
        try:
            root = ET.fromstring(xml_content)
            
            # Define namespaces
            namespaces = {
                'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'
            }
            
            # Check if this is a sitemap index (contains sitemaps)
            sitemaps = root.findall('.//sm:sitemap/sm:loc', namespaces)
            if sitemaps:
                logger.info(f"Found sitemap index with {len(sitemaps)} sitemaps")
                for sitemap_elem in sitemaps:
                    sitemap_loc = sitemap_elem.text
                    if sitemap_loc:
                        logger.info(f"Parsing sub-sitemap: {sitemap_loc}")
                        try:
                            sub_urls = self.parse_sitemap(sitemap_loc)
                            urls.update(sub_urls)
                        except Exception as e:
                            logger.warning(f"Failed to parse sub-sitemap {sitemap_loc}: {e}")
                return urls
            
            # Extract URLs from regular sitemap
            url_elements = root.findall('.//sm:url/sm:loc', namespaces)
            
            # Fallback: try without namespace
            if not url_elements:
                url_elements = root.findall('.//url/loc')
            
            logger.info(f"Found {len(url_elements)} URL entries")
            
            for url_elem in url_elements:
                url = url_elem.text
                if url:
                    urls.add(url.strip())
            
            return urls
            
        except Exception as e:
            logger.error(f"Error parsing XML: {e}")
            raise


# Global sitemap crawler instance
_sitemap_crawler: SitemapCrawlerService = None


def get_sitemap_crawler() -> SitemapCrawlerService:
    """Get or create the global SitemapCrawlerService instance"""
    global _sitemap_crawler
    
    if _sitemap_crawler is None:
        _sitemap_crawler = SitemapCrawlerService()
    
    return _sitemap_crawler
