import hashlib
import os
from typing import List
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from .models import ScrapedItem

class RealScraper(BaseScraper):
    """Extraction strategy for quotes.toscrape.com with screenshot recording."""
    
    def parse_logic(self, soup: BeautifulSoup, url: str) -> List[ScrapedItem]:
        items_map = {}
        
        # Take a screenshot to "record" the process
        screenshot_path = os.path.abspath('artifacts/quotes_demo.png')
        if not os.path.exists('artifacts'):
            os.makedirs('artifacts')
        self.driver.save_screenshot(screenshot_path)
        
        # Collect Quotes
        for quote_block in soup.find_all("div", class_="quote"):
            text_el = quote_block.find("span", class_="text")
            author_el = quote_block.find("small", class_="author")
            
            if text_el and author_el:
                text = text_el.get_text(strip=True)
                author = author_el.get_text(strip=True)
                
                hash_id = hashlib.md5(f"{url}_quote_{text[:30]}".encode()).hexdigest()
                items_map[hash_id] = ScrapedItem(
                    id=hash_id, 
                    url=url, 
                    element_type="quote", 
                    text=f"{text} - {author}"
                )

        # Collect Links
        for tag_el in soup.find_all("a", class_="tag"):
            tag_text = tag_el.get_text(strip=True)
            tag_href = tag_el.get('href')
            
            hash_id = hashlib.md5(f"{url}_tag_{tag_text}".encode()).hexdigest()
            items_map[hash_id] = ScrapedItem(
                id=hash_id, 
                url=url, 
                element_type="tag_link", 
                text=tag_text, 
                href=f"https://quotes.toscrape.com{tag_href}"
            )

        return list(items_map.values())
