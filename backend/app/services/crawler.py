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
        """
        Crawl website using a BFS strategy with strict token and page limits.
        
        Strategy:
        1. Crawl root page (Level 0).
        2. Extract Level 1 links (limit 20).
        3. Crawl Level 1 pages.
        4. If token space remains, crawl Level 2 pages (links found on Level 1).
        5. Stop when token limit (50k) is reached or no more links.
        """
        MAX_TOKENS = 50000
        LEVEL_1_LIMIT = 20
        
        crawled_pages = []
        visited_urls = set()
        total_tokens = 0
        
        # Queue stores: (url, level)
        # Using a list as a simple queue for BFS
        queue = [(url, 0)]
        visited_urls.add(url)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                
                while queue:
                    if total_tokens >= MAX_TOKENS:
                        print("Token limit reached. Stopping crawl.")
                        break
                        
                    current_url, level = queue.pop(0)
                    
                    # Crawl the page
                    print(f"Crawling {current_url} (Level {level})")
                    page_data = await self._crawl_page(client, current_url)
                    
                    if not page_data:
                        continue
                        
                    # Calculate tokens (approx 4 chars per token)
                    content_len = len(page_data.get('content', ''))
                    page_tokens = content_len // 4
                    
                    # If this single page exceeds the remaining limit, we might still include it 
                    # if it's the first page, or maybe we truncate? 
                    # User said "accumulate until 50k". Let's update total.
                    total_tokens += page_tokens
                    crawled_pages.append(page_data)
                    
                    # Stop if we just exceeded limit
                    if total_tokens >= MAX_TOKENS:
                        break
                    
                    # Logic for adding next level links
                    # Level 0 -> adds Level 1 (limit 20)
                    # Level 1 -> adds Level 2 (unlimited count, but bounded by global token/page limits mostly)
                    # User said: "Then if window allows, go to links inside those pages".
                    
                    # We usually don't go deeper than Level 2 based on the description, 
                    # but "iterate until links end or 50k tokens" implies potential depth, 
                    # yet "1st level links... then links inside those" sounds like 2 levels depth.
                    # I will allow Level 2.
                    
                    if level < 2:
                        raw_html = page_data.get('raw_html', '')
                        internal_links = self._extract_internal_links(current_url, raw_html)
                        
                        # Prioritize is good, but for Level 0 we specifically need to limit to 20
                        if level == 0:
                            # Prioritize to get the "best" 20 links
                            prioritized = self._prioritize_links(internal_links, raw_html)
                            # Take top 20 unique that haven't been visited
                            count_added = 0
                            for link in prioritized:
                                if link not in visited_urls:
                                    if count_added < LEVEL_1_LIMIT:
                                        visited_urls.add(link)
                                        queue.append((link, level + 1))
                                        count_added += 1
                        else:
                            # For Level 1 -> Level 2, we just add them all (BFS will handle order)
                            # We might want to prioritize them too?
                            # sticking to simple order or prioritization
                            prioritized = self._prioritize_links(internal_links, raw_html)
                            for link in prioritized:
                                if link not in visited_urls:
                                    visited_urls.add(link)
                                    queue.append((link, level + 1))
            
            return crawled_pages

        except Exception as e:
            print(f"Error during crawl website {url}: {e}")
            # Return whatever we managed to crawl
            return crawled_pages
    
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
    
    async def validate_url(self, url: str) -> tuple[bool, str]:
        """Validate if URL is accessible. Returns (is_valid, error_message)."""
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                response = await client.head(url)
                
                if response.status_code < 400:
                    return True, ""
                elif response.status_code == 403:
                    return False, "This website is protected and blocking our access. Please check if the site allows external crawlers."
                elif response.status_code == 401:
                    return False, "This website requires authentication. We can only analyze publicly accessible pages."
                elif response.status_code == 404:
                    return False, "The page was not found. Please check the URL and try again."
                elif response.status_code == 503:
                    return False, "The website is temporarily unavailable. Please try again later."
                elif response.status_code >= 500:
                    return False, "The website is experiencing server issues. Please try again later."
                else:
                    return False, f"Unable to access the website (HTTP {response.status_code}). Please verify the URL is correct."
                    
        except httpx.TimeoutException:
            return False, "The website took too long to respond. Please check if the site is online and try again."
        except httpx.ConnectError:
            return False, "Could not connect to the website. Please verify the URL is correct and the site is online."
        except httpx.TooManyRedirects:
            return False, "The website has too many redirects. Please check the URL and try again."
        except Exception:
            return False, "Unable to reach the website. Please verify the URL is correct and accessible."
