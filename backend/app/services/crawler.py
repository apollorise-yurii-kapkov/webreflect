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
        """Crawl website and extract content from multiple pages using breadth-first approach."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Get main page first
                main_page = await self._crawl_page(client, url)
                if not main_page:
                    return []
                
                pages = [main_page]
                crawled_urls = {url}
                
                # Breadth-first crawling by levels
                current_level_urls = [url]
                level = 0
                
                while len(pages) < self.max_pages and current_level_urls and level < 3:  # Max 3 levels deep
                    next_level_urls = []
                    
                    # Process all URLs at current level
                    for current_url in current_level_urls:
                        if len(pages) >= self.max_pages:
                            break
                            
                        # Get page content if not already crawled
                        if current_url not in crawled_urls:
                            try:
                                page = await self._crawl_page(client, current_url)
                                if page:
                                    pages.append(page)
                                    crawled_urls.add(current_url)
                                    
                                    # Extract links for next level
                                    internal_links = self._extract_internal_links(current_url, page.get('raw_html', ''))
                                    for link in internal_links:
                                        if link not in crawled_urls and link not in next_level_urls:
                                            next_level_urls.append(link)
                            except Exception as e:
                                print(f"Error crawling page {current_url}: {e}")
                                # Continue to next page instead of stopping
                                continue
                        else:
                            # Still extract links from already crawled pages for next level
                            for page in pages:
                                if page.get('url') == current_url:
                                    internal_links = self._extract_internal_links(current_url, page.get('raw_html', ''))
                                    for link in internal_links:
                                        if link not in crawled_urls and link not in next_level_urls:
                                            next_level_urls.append(link)
                                    break
                    
                    # Move to next level
                    current_level_urls = next_level_urls[:self.max_pages - len(pages)]  # Limit URLs per level
                    level += 1
                
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
            # Return None to skip this page and continue with others
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
                
                # Only include internal links, exclude fragments, files, and special links
                if (parsed_url.netloc == base_domain and 
                    not href.startswith('#') and 
                    not href.startswith('mailto:') and
                    not href.startswith('tel:') and
                    not any(full_url.lower().endswith(ext) for ext in ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.doc', '.docx'])):
                    # Clean URL by removing fragments and query params for deduplication
                    clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                    if clean_url.endswith('/'):
                        clean_url = clean_url.rstrip('/')
                    links.add(clean_url or full_url)
            
            return list(links)
            
        except Exception as e:
            print(f"Error extracting links: {e}")
            return []
    
    async def _get_sitemap_urls(self, client: httpx.AsyncClient, base_url: str) -> List[str]:
        """Try to fetch and parse sitemap.xml for comprehensive page discovery."""
        sitemap_urls = []
        
        # Common sitemap locations
        sitemap_paths = ['/sitemap.xml', '/sitemap_index.xml', '/robots.txt']
        
        for path in sitemap_paths:
            try:
                sitemap_url = urljoin(base_url, path)
                response = await client.get(sitemap_url, timeout=10)
                
                if response.status_code == 200:
                    if path == '/robots.txt':
                        # Extract sitemap URLs from robots.txt
                        for line in response.text.split('\n'):
                            if line.lower().startswith('sitemap:'):
                                sitemap_url = line.split(':', 1)[1].strip()
                                sitemap_response = await client.get(sitemap_url, timeout=10)
                                if sitemap_response.status_code == 200:
                                    sitemap_urls.extend(self._parse_sitemap_xml(sitemap_response.text, base_url))
                    else:
                        # Parse XML sitemap
                        sitemap_urls.extend(self._parse_sitemap_xml(response.text, base_url))
                    
                    if sitemap_urls:
                        break  # Found sitemap, no need to try others
                        
            except Exception as e:
                print(f"Error fetching sitemap {path}: {e}")
                continue
        
        return sitemap_urls[:15]  # Limit sitemap URLs
    
    def _parse_sitemap_xml(self, xml_content: str, base_url: str) -> List[str]:
        """Parse sitemap XML and extract URLs."""
        urls = []
        try:
            soup = BeautifulSoup(xml_content, 'xml')
            base_domain = urlparse(base_url).netloc
            
            # Handle regular sitemap
            for url_tag in soup.find_all('url'):
                loc_tag = url_tag.find('loc')
                if loc_tag and loc_tag.text:
                    url = loc_tag.text.strip()
                    parsed_url = urlparse(url)
                    if parsed_url.netloc == base_domain:
                        urls.append(url)
            
            # Handle sitemap index
            for sitemap_tag in soup.find_all('sitemap'):
                loc_tag = sitemap_tag.find('loc')
                if loc_tag and loc_tag.text:
                    # Could recursively fetch sub-sitemaps, but keep it simple for now
                    pass
                    
        except Exception as e:
            print(f"Error parsing sitemap XML: {e}")
        
        return urls
    
    def _prioritize_links(self, links: List[str], html: str) -> List[str]:
        """Prioritize links based on navigation menus and importance."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            prioritized = []
            regular = []
            
            # Find navigation elements
            nav_selectors = [
                'nav a', 'header nav a', '.navbar a', '.navigation a', 
                '.menu a', '.main-menu a', '#menu a', '#navigation a',
                '[role="navigation"] a', '.nav a', '.primary-nav a'
            ]
            
            nav_links = set()
            base_domain = urlparse(links[0] if links else '').netloc
            
            for selector in nav_selectors:
                for link in soup.select(selector):
                    href = link.get('href')
                    if href:
                        full_url = urljoin(links[0] if links else '', href)
                        parsed_url = urlparse(full_url)
                        # Only add links from the same domain
                        if parsed_url.netloc == base_domain:
                            nav_links.add(full_url)
            
            # Categorize links
            for link in links:
                if link in nav_links:
                    prioritized.append(link)
                else:
                    # Prioritize common important pages
                    path = urlparse(link).path.lower()
                    if any(keyword in path for keyword in [
                        'about', 'services', 'products', 'contact', 'pricing', 
                        'features', 'solutions', 'company', 'team', 'careers'
                    ]):
                        prioritized.append(link)
                    else:
                        regular.append(link)
            
            return prioritized + regular
            
        except Exception as e:
            print(f"Error prioritizing links: {e}")
            return links
    
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
