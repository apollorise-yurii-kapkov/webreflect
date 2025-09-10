from typing import List, Dict, Optional
import asyncio
from urllib.parse import urljoin, urlparse
import re
import httpx
from bs4 import BeautifulSoup

from app.core.config import settings
from app.schemas.analysis import CrawledPageResponse


class WebsiteCrawler:
    """Website crawler service using httpx and BeautifulSoup."""
    
    def __init__(self):
        self.max_pages = settings.MAX_PAGES_PER_SITE
        self.timeout = settings.CRAWL_TIMEOUT
        self.max_content_length = settings.MAX_CONTENT_LENGTH
    
    async def crawl_website(self, url: str) -> List[Dict]:
        """Crawl website and extract content from multiple pages."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Get main page first
                main_page = await self._crawl_page(client, url)
                if not main_page:
                    return []
                
                pages = [main_page]
                
                # Extract internal links from main page
                internal_links = self._extract_internal_links(url, main_page.get('raw_html', ''))
                
                # Crawl additional pages (limited)
                for link in internal_links[:self.max_pages - 1]:
                    try:
                        page = await self._crawl_page(client, link)
                        if page:
                            pages.append(page)
                    except Exception as e:
                        print(f"Error crawling {link}: {e}")
                        continue
                
                return pages
                
        except Exception as e:
            print(f"Error crawling website {url}: {e}")
            return []
    
    async def _crawl_page(self, client: httpx.AsyncClient, url: str) -> Optional[Dict]:
        """Crawl a single page and extract content."""
        try:
            # Fetch the page
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract clean text content
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            clean_content = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in clean_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_content = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit content length
            if len(clean_content) > self.max_content_length:
                clean_content = clean_content[:self.max_content_length] + "..."
            
            # Extract title
            title = None
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()
            
            # Extract meta description
            meta_desc = None
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                meta_desc = meta_tag.get('content', '').strip()
            
            # Extract H1 tags
            h1_tags = [h1.get_text().strip() for h1 in soup.find_all('h1')]
            
            # Extract CTA texts (buttons, links with action words)
            cta_texts = self._extract_cta_texts(soup)
            
            return {
                'url': url,
                'title': title,
                'content': clean_content,
                'meta_description': meta_desc,
                'h1_tags': h1_tags,
                'cta_texts': cta_texts,
                'raw_html': response.text
            }
            
        except Exception as e:
            print(f"Error crawling page {url}: {e}")
            return None
    
    def _extract_internal_links(self, base_url: str, html: str) -> List[str]:
        """Extract internal links from HTML."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            base_domain = urlparse(base_url).netloc
            links = set()
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(base_url, href)
                parsed_url = urlparse(full_url)
                
                # Only include internal links
                if (parsed_url.netloc == base_domain and 
                    not href.startswith('#') and 
                    not href.startswith('mailto:') and
                    not href.startswith('tel:')):
                    links.add(full_url)
            
            return list(links)
            
        except Exception as e:
            print(f"Error extracting links: {e}")
            return []
    
    def _extract_cta_texts(self, soup: BeautifulSoup) -> List[str]:
        """Extract Call-to-Action texts from the page."""
        cta_texts = []
        
        # Common CTA selectors
        cta_selectors = [
            'button',
            'a[class*="btn"]',
            'a[class*="button"]',
            'a[class*="cta"]',
            'input[type="submit"]',
            '[class*="call-to-action"]'
        ]
        
        # Action words that indicate CTAs
        action_words = [
            'get', 'start', 'try', 'buy', 'shop', 'order', 'download', 
            'sign up', 'register', 'subscribe', 'join', 'contact', 'learn',
            'discover', 'explore', 'book', 'schedule', 'request', 'claim'
        ]
        
        for selector in cta_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text().strip()
                if text and len(text) < 100:  # Reasonable CTA length
                    cta_texts.append(text)
        
        # Also look for links with action words
        for link in soup.find_all('a'):
            text = link.get_text().strip().lower()
            if any(word in text for word in action_words) and len(text) < 50:
                cta_texts.append(link.get_text().strip())
        
        # Remove duplicates and return
        return list(set(cta_texts))
    
    async def validate_url(self, url: str) -> bool:
        """Validate if URL is accessible."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.head(url)
                return response.status_code < 400
        except:
            return False
