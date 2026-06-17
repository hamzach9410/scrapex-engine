import hashlib
from typing import List
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from .models import ScrapedItem

class NztaScraper(BaseScraper):
    """Deep extraction strategy for nzta.govt.nz"""
    
    def parse_logic(self, soup: BeautifulSoup, url: str) -> List[ScrapedItem]:
        items = []
        
        # 1. Collect all Headings (h1 to h6)
        for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            text = heading.get_text(strip=True)
            if text:
                hash_id = hashlib.md5(f"{url}_heading_{text}".encode()).hexdigest()
                items.append(ScrapedItem(id=hash_id, url=url, element_type=heading.name, text=text))
                
        # 2. Collect all meaningful Paragraphs
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if text and len(text) > 10:  # Filter out empty/trivial blocks
                hash_id = hashlib.md5(f"{url}_paragraph_{text[:30]}".encode()).hexdigest()
                items.append(ScrapedItem(id=hash_id, url=url, element_type="paragraph", text=text))
                
        # 3. Collect all Links
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True) or "No Text"
            href = a['href']
            
            # Convert relative links to absolute if they start with /
            if href.startswith('/'):
                href = self.base_url.rstrip('/') + href
                
            hash_id = hashlib.md5(f"{url}_link_{href}_{text}".encode()).hexdigest()
            items.append(ScrapedItem(id=hash_id, url=url, element_type="link", text=text, href=href))

        # 4. Collect List Items
        for li in soup.find_all("li"):
            text = li.get_text(strip=True)
            if text and len(text) > 5:
                hash_id = hashlib.md5(f"{url}_li_{text[:30]}".encode()).hexdigest()
                items.append(ScrapedItem(id=hash_id, url=url, element_type="list_item", text=text))

        return items
