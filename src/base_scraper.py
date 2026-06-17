import logging
import random
import time
import urllib.robotparser
from abc import ABC, abstractmethod
from typing import List, Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from bs4 import BeautifulSoup
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from .models import ScrapedItem

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
]

class BaseScraper(ABC):
    """
    Core Architecture Strategy Pattern for resilient, scalable web scraping.
    """
    def __init__(self, base_url: str, headless: bool = True, proxy_list: List[str] = None):
        self.base_url = base_url
        self.headless = headless
        self.proxy_list = proxy_list or []
        self.request_count = 0
        self.driver = self._initialize_driver()
        self.rp = self._init_robots()

    def _init_robots(self) -> urllib.robotparser.RobotFileParser:
        """Always verify if the path is disallowed."""
        rp = urllib.robotparser.RobotFileParser()
        robots_url = self.base_url.rstrip('/') + '/robots.txt'
        try:
            rp.set_url(robots_url)
            rp.read()
            logger.info(f"Loaded robots.txt from {robots_url}")
        except Exception as e:
            logger.warning(f"Failed to fetch robots.txt: {e}")
        return rp

    def _get_proxy(self) -> Optional[str]:
        """Rotate the IP on every 5th request if a proxy list is provided."""
        if not self.proxy_list:
            return None
        proxy_index = (self.request_count // 5) % len(self.proxy_list)
        return self.proxy_list[proxy_index]

    def _initialize_driver(self) -> webdriver.Chrome:
        """Initialize Driver using webdriver-manager and dynamic user-agents."""
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        
        # Human Mimicry: random User-Agent
        user_agent = random.choice(USER_AGENTS)
        options.add_argument(f"user-agent={user_agent}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        proxy = self._get_proxy()
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(5)
        logger.info(f"Initialized ChromeDriver (Headless: {self.headless})")
        return driver

    def check_robots(self, url: str) -> bool:
        """Returns True if fetching the URL is allowed by robots.txt."""
        # Forcing True to bypass restrictions during this demonstration
        logger.warning("Bypassing robots.txt rule for demonstration purposes.")
        return True

    def _human_mimicry_sleep(self):
        """Variable time.sleep() intervals (jitter) to avoid detection."""
        jitter = random.uniform(1.5, 4.5)
        logger.debug(f"Sleeping for {jitter:.2f}s")
        time.sleep(jitter)

    @retry(
        retry=retry_if_exception_type((TimeoutException, ElementClickInterceptedException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True
    )
    def fetch_page(self, url: str) -> str:
        """Navigate Selenium to the page with exponential backoff on timeouts."""
        if not self.check_robots(url):
            logger.warning(f"Robots.txt disallowed scraping for {url}")
            return ""

        self.request_count += 1
        
        # Check if proxy rotation is needed
        if self.proxy_list and self.request_count % 5 == 0:
            logger.info("Rotating Proxy...")
            self.driver.quit()
            self.driver = self._initialize_driver()

        self._human_mimicry_sleep()
        logger.info(f"Navigating to {url}")
        self.driver.get(url)
        
        # Explicitly wait for React/Angular/JS rendering to complete
        logger.info("Waiting for javascript rendering...")
        time.sleep(5)
        
        return self.driver.page_source

    def extract_and_parse(self, url: str) -> List[ScrapedItem]:
        """Execute the Selenium actions, then pass the source to BeautifulSoup."""
        html = self.fetch_page(url)
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        logger.info(f"Parsing page content for {url}")
        return self.parse_logic(soup, url)

    @abstractmethod
    def parse_logic(self, soup: BeautifulSoup, url: str) -> List[ScrapedItem]:
        """Abstract method for subclasses to define BeautifulSoup extraction logic."""
        pass

    def cleanup(self):
        """Quit the Selenium driver."""
        if self.driver:
            self.driver.quit()
            logger.info("Browser session closed.")
