# ScrapeX Engine

A senior-level Python framework for building resilient, scalable web scrapers. Combines **Selenium**, **BeautifulSoup4**, and **Tenacity** into a production-ready data extraction pipeline with built-in stealth, retry logic, schema validation, and deduplication.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Selenium](https://img.shields.io/badge/Selenium-4.10+-green?logo=selenium)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Features

- **Strategy Pattern Architecture** — Extend by inheriting from `BaseScraper` for any target website
- **Stealth & Anti-Bot** — Random User-Agent rotation, proxy IP rotation every 5 requests, human-mimicry jitter delays
- **Auto Retry** — `tenacity` exponential backoff on `TimeoutException` and `ElementClickInterceptedException`
- **Robots.txt Compliance** — Automatically reads and respects `robots.txt` before crawling
- **Schema Validation** — Pydantic v2 enforces strict data integrity on every extracted item
- **Deduplication Pipeline** — MD5 hash-based deduplication before saving to SQLite
- **Screenshot Recording** — Saves a screenshot of the scraped page as proof of execution
- **CSV Export** — Automatically exports results to `exported_data.csv` alongside SQLite storage

---

## Project Structure

```
├── src/
│   ├── __init__.py
│   ├── base_scraper.py      # Abstract core — Selenium, stealth, retries, robots.txt
│   ├── database.py          # SQLite manager with Pandas deduplication
│   ├── models.py            # Pydantic v2 schema for ScrapedItem
│   ├── real_scraper.py      # Live scraper targeting quotes.toscrape.com
│   ├── example_scraper.py   # Minimal example implementation
│   └── nzta_scraper.py      # NZTA-specific scraper strategy
├── artifacts/
│   └── quotes_demo.png      # Auto-generated screenshot on each run
├── main.py                  # Pipeline entry point
├── requirements.txt
└── .gitignore
```

---

## Installation

**Requirements:** Python 3.8+, Google Chrome installed

```bash
git clone https://github.com/hamzach9410/scrapex-engine.git
cd scrapex-engine
pip install -r requirements.txt
```

> `webdriver-manager` auto-downloads the correct ChromeDriver — no manual setup needed.

---

## Usage

```bash
python main.py
```

This scrapes [quotes.toscrape.com](https://quotes.toscrape.com), validates the data, deduplicates, saves to `scraper_data.sqlite`, and exports `exported_data.csv`.

---

## Building a Custom Scraper

Create a new class inheriting from `BaseScraper` and override `parse_logic()`:

```python
from bs4 import BeautifulSoup
from typing import List
from src.base_scraper import BaseScraper
from src.models import ScrapedItem

class MyScraper(BaseScraper):
    def parse_logic(self, soup: BeautifulSoup, url: str) -> List[ScrapedItem]:
        # Your BeautifulSoup extraction logic here
        pass
```

Hook it up in `main.py`:

```python
scraper = MyScraper(base_url="https://yoursite.com", headless=True)
items = scraper.extract_and_parse("https://yoursite.com/page")
db_manager.save_items(items, export_csv=True)
```

---

## Configuration

| Parameter | Default | Description |
|---|---|---|
| `headless` | `True` | Run Chrome invisibly in background |
| `proxy_list` | `[]` | List of proxy strings for IP rotation |
| `base_url` | required | Target website base URL |

**Watch the scraper live (disable headless):**

```python
scraper = RealScraper(base_url="https://quotes.toscrape.com/", headless=False)
```

---

## Tech Stack

| Library | Version | Role |
|---|---|---|
| `selenium` | >=4.10.0 | Browser automation |
| `beautifulsoup4` | >=4.12.0 | HTML parsing |
| `webdriver-manager` | >=4.0.0 | Auto ChromeDriver management |
| `pydantic` | >=2.0.0 | Data schema validation |
| `pandas` | >=2.0.0 | Deduplication & CSV export |
| `tenacity` | >=8.2.0 | Retry with exponential backoff |

---

## License

MIT
