import hashlib
from typing import List
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from .models import ScrapedItem

class ExampleScraper(BaseScraper):
    """Concrete implementation for example.com following the Strategy Pattern."""
    
    def parse_logic(self, soup: BeautifulSoup, url: str) -> List[ScrapedItem]:
        """Extract data using BeautifulSoup."""
        items = []
        
        # Example extracting h1 tags
        headings = soup.find_all("h1")
        for idx, heading in enumerate(headings):
            title = heading.get_text(strip=True)
            
            # Generate a unique hash for deduplication
            hash_id = hashlib.md5(f"{url}_{idx}_{title}".encode()).hexdigest()
            
            item = ScrapedItem(
                id=hash_id,
                url=url,
                title=title
            )
            items.append(item)
            
        return items
