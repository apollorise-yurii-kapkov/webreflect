from typing import List, Dict, Optional
import asyncio
from urllib.parse import urljoin, urlparse
import re
import httpx
from bs4 import BeautifulSoup

from app.core.config import settings


class WebsiteCrawler:
    """Crawls a website breadth‑first up to a limited number of pages."""

    def __init__(self):
        self.max_pages = settings.MAX_PAGES_PER_SITE
        self.timeout = settings.CRAWL_TIMEOUT
        self.max_content_length = settings.MAX_CONTENT_LENGTH

    async def crawl_website(self, url: str) -> List[Dict]:
        """Breadth‑first crawl to max_pages depth, using sitemap if available."""
        try:
            base = self._normalize_url(url)
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                main_page = await self._crawl_page(client, base)
                if not main_page:
                    return []
                pages = [main_page]
                crawled = {base}

                level_urls = await self._get_sitemap_urls(client, base)
                if not level_urls:
                    level_urls = self._extract_internal_links(base, main_page.get("raw_html", ""))
                    level_urls = self._prioritize_links(level_urls, main_page.get("raw_html", ""))
                level = 0

                while len(pages) < self.max_pages and level_urls and level < 3:
                    next_level = []
                    fetch_tasks = [self._crawl_page(client, u) for u in level_urls if u not in crawled]
                    for task in asyncio.as_completed(fetch_tasks):
                        if len(pages) >= self.max_pages:
                            break
                        try:
                            page = await task
                            if not page:
                                continue
                            pages.append(page)
                            url_cur = page["url"]
                            crawled.add(url_cur)
                            internal = self._extract_internal_links(url_cur, page.get("raw_html", ""))
                            next_level.extend(internal)
                        except Exception as e:
                            print(f"Error crawling page: {e}")
                    next_level = list(dict.fromkeys(next_level))
                    level_urls = next_level[:max(0, self.max_pages - len(pages))]
                    level += 1
            return pages
        except Exception as e:
            print(f"Error crawling website {url}: {e}")
            return []

    async def _crawl_page(self, client: httpx.AsyncClient, url: str) -> Optional[Dict]:
        """Fetch and parse a single page, returning extracted info."""
        try:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            text = soup.get_text(separator=" ")
            text = re.sub(r"\s+", " ", text).strip()
            if len(text) > self.max_content_length:
                text = text[:self.max_content_length] + "..."
            title = soup.title.get_text().strip() if soup.title else None
            meta_desc_tag = soup.find("meta", attrs={"name": "description"})
            meta_desc = meta_desc_tag.get("content").strip() if meta_desc_tag and meta_desc_tag.get("content") else None
            h1_tags = [h1.get_text().strip() for h1 in soup.find_all("h1")]
            cta_texts = self._extract_cta_texts(soup)
            return {
                "url": url,
                "title": title,
                "content": text,
                "meta_description": meta_desc,
                "h1_tags": h1_tags,
                "cta_texts": cta_texts,
                "raw_html": response.text,
            }
        except Exception as e:
            print(f"Error crawling page {url}: {e}")
            return None

    def _extract_internal_links(self, base_url: str, html: str) -> List[str]:
        """Return unique internal links from html."""
        try:
            soup = BeautifulSoup(html, "html.parser")
            base = urlparse(base_url)
            links = []
            for link in soup.find_all("a", href=True):
                href = link["href"]
                full_url = urljoin(base_url, href)
                parsed = urlparse(full_url)
                if parsed.netloc == base.netloc and \
                   not href.startswith(("#", "mailto:", "tel:")) and \
                   not re.search(r"\.(pdf|jpg|jpeg|png|gif|zip|doc|docx)$", parsed.path, re.I):
                    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
                    links.append(clean_url)
            return list(dict.fromkeys(links))
        except Exception as e:
            print(f"Error extracting links: {e}")
            return []

    async def _get_sitemap_urls(self, client: httpx.AsyncClient, base_url: str) -> List[str]:
        """Try to retrieve sitemap urls from common locations or robots.txt."""
        urls = []
        for path in ["/sitemap.xml", "/sitemap_index.xml", "/robots.txt"]:
            try:
                sitemap_url = urljoin(base_url, path)
                resp = await client.get(sitemap_url, timeout=10)
                if resp.status_code == 200:
                    if path == "/robots.txt":
                        for line in resp.text.splitlines():
                            if line.lower().startswith("sitemap:"):
                                sitemap_link = line.split(":", 1)[1].strip()
                                sm_resp = await client.get(sitemap_link, timeout=10)
                                if sm_resp.status_code == 200:
                                    urls.extend(self._parse_sitemap_xml(sm_resp.text, base_url))
                    else:
                        urls.extend(self._parse_sitemap_xml(resp.text, base_url))
                    if urls:
                        break
            except Exception as e:
                print(f"Error fetching sitemap {path}: {e}")
                continue
        return urls[:15]

    def _parse_sitemap_xml(self, xml_content: str, base_url: str) -> List[str]:
        """Parse xml sitemap for urls within base domain."""
        results = []
        try:
            soup = BeautifulSoup(xml_content, "xml")
            base_netloc = urlparse(base_url).netloc
            for url_tag in soup.find_all("url"):
                loc = url_tag.find("loc")
                if loc and loc.text:
                    parsed = urlparse(loc.text.strip())
                    if parsed.netloc == base_netloc:
                        results.append(loc.text.strip().rstrip("/"))
        except Exception as e:
            print(f"Error parsing sitemap XML: {e}")
        return list(dict.fromkeys(results))

    def _prioritize_links(self, links: List[str], html: str) -> List[str]:
        """Move nav and important pages to front of list."""
        try:
            soup = BeautifulSoup(html, "html.parser")
            nav_selectors = [
                "nav a", "header nav a", ".navbar a", ".navigation a", ".menu a",
                ".main-menu a", "#menu a", "#navigation a", '[role=\"navigation\"] a', '.nav a', '.primary-nav a'
            ]
            nav_links = set()
            for selector in nav_selectors:
                for tag in soup.select(selector):
                    href = tag.get("href")
                    if href:
                        nav_links.add(urljoin(links[0] if links else "", href))
            prioritized, others = [], []
            important_keywords = (
                "about", "services", "products", "contact", "pricing",
                "features", "solutions", "company", "team", "careers"
            )
            seen = set()
            for link in links:
                if link in seen:
                    continue
                seen.add(link)
                path = urlparse(link).path.lower()
                if link in nav_links or any(k in path for k in important_keywords):
                    prioritized.append(link)
                else:
                    others.append(link)
            return prioritized + others
        except Exception as e:
            print(f"Error prioritizing links: {e}")
            return links

    def _extract_cta_texts(self, soup: BeautifulSoup) -> List[str]:
        """Extract call-to-action texts from buttons and links."""
        cta_texts = []
        selectors = [
            "button",
            "a[class*=\"btn\"]",
            "a[class*=\"button\"]",
            "a[class*=\"cta\"]",
            "input[type=\"submit\"]",
            "[class*=\"call-to-action\"]",
        ]
        action_words = [
            "get", "start", "try", "buy", "shop", "order", "download",
            "sign up", "register", "subscribe", "join", "contact", "learn",
            "discover", "explore", "book", "schedule", "request", "claim",
        ]
        for selector in selectors:
            for element in soup.select(selector):
                text = element.get_text().strip()
                if text and len(text) < 100:
                    cta_texts.append(text)
        for link in soup.find_all("a"):
            text = link.get_text().strip()
            lower = text.lower()
            if text and any(word in lower for word in action_words) and len(text) < 50:
                cta_texts.append(text)
        return list(dict.fromkeys(cta_texts))

    async def validate_url(self, url: str) -> bool:
        """Check if url is accessible."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.head(self._normalize_url(url))
                return resp.status_code < 400
        except Exception:
            return False

    def _normalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        if not parsed.scheme:
            return "https://" + url
        return url
