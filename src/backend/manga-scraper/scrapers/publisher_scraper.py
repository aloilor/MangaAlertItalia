import requests
import logging

logger = logging.getLogger(__name__)

class PublisherScraper:
    """Base class for scraping different manga publishers' websites"""

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        )
    }
    timeout = 30

    def __init__(self, manga: str, url: str):
        self.manga = manga
        self.url = url

    def scrape(self, params=None):
        """Scrapes the URL and returns the HTML response"""
        try:
            response = requests.get(
                self.url,
                headers=self.headers,
                params=params,
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.text
            else:
                logger.error(
                    f"Received status code {response.status_code} while scraping {self.manga}"
                )
                return None
        except requests.RequestException as e:
            logger.error(f"Exception while fetching {self.manga}: {e}")
            return None

    def parse(self, response: str):
        """Abstract method for parsing the response; to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement the 'parse' method")
