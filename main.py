import logging
from src.real_scraper import RealScraper
from src.database import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting ScrapeX Engine Demo on Real Website...")
    
    # 1. Initialize Pipeline components
    db_manager = DatabaseManager()
    
    # 2. Initialize Scraper (Strategy Pattern)
    # Headless is False so we can see the execution visually
    scraper = RealScraper(base_url="https://quotes.toscrape.com/", headless=False)
    
    try:
        # 3. Extract & Parse
        target_url = "https://quotes.toscrape.com/"
        scraped_items = scraper.extract_and_parse(target_url)
        
        logger.info(f"Extracted {len(scraped_items)} items from {target_url}")
        
        # 4. Filter, Validate & Save
        db_manager.save_items(scraped_items, export_csv=True)
        
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()
