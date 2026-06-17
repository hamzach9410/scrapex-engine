import sqlite3
import pandas as pd
import logging
from typing import List
from .models import ScrapedItem

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "scraper_data.sqlite"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database with an expanded table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comprehensive_data (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                element_type TEXT,
                text TEXT,
                href TEXT,
                scraped_at TEXT
            )
        ''')
        conn.commit()
        conn.close()
        logger.debug(f"Initialized database table comprehensive_data at {self.db_path}")

    def deduplicate(self, items: List[ScrapedItem]) -> List[ScrapedItem]:
        if not items:
            return []
            
        conn = sqlite3.connect(self.db_path)
        existing_ids = set()
        
        placeholders = ','.join(['?'] * len(items))
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM comprehensive_data WHERE id IN ({placeholders})", [item.id for item in items])
        for row in cursor.fetchall():
            existing_ids.add(row[0])
            
        conn.close()
        
        new_items = [item for item in items if item.id not in existing_ids]
        logger.info(f"Deduplication complete: {len(items)} total, {len(new_items)} new items.")
        return new_items

    def save_items(self, items: List[ScrapedItem], export_csv: bool = False):
        new_items = self.deduplicate(items)
        if not new_items:
            logger.info("No new items to save.")
            return

        df = pd.DataFrame([item.model_dump(exclude={'raw_html'}) for item in new_items])
        if 'scraped_at' in df.columns:
            df['scraped_at'] = df['scraped_at'].astype(str)
        
        conn = sqlite3.connect(self.db_path)
        df.to_sql('comprehensive_data', conn, if_exists='append', index=False)
        conn.close()
        logger.info(f"Saved {len(df)} items to comprehensive_data table.")
        
        if export_csv:
            df.to_csv("exported_data.csv", index=False)
            logger.info("Exported to exported_data.csv")
