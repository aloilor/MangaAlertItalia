from .publisher_scraper import PublisherScraper
from models.manga_release import MangaRelease
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class StarComicsScraper(PublisherScraper):
    """Scraper for Star Comics publisher"""

    base_url = "https://www.starcomics.com"

    def parse(self, response: str):
        if response is None:
            logger.error(f"No response for '{self.manga}' from 'Star Comics'")
            return None

        soup = BeautifulSoup(response, "html.parser")
        latest_item = soup.find("div", class_="fumetto-card")

        if latest_item:
            title_elem = latest_item.find("h4", class_="card-title")
            link_elem = latest_item.find("a")
            date_elem = latest_item.find("p", class_="card-text").find(
                "span", class_="text-secondary"
            )

            title = title_elem.get_text(strip=True) if title_elem else ""
            link = self.base_url + link_elem["href"] if link_elem and link_elem.get("href") else ""
            release_date = date_elem.get_text(strip=True) if date_elem else ""

            if title and link and release_date:
                return MangaRelease(title, link, release_date, "star_comics")
            else:
                logger.error(f"Missing data in response for '{self.manga}' from 'Star Comics'")
                return None

        logger.error(f"No results found for '{self.manga}' from 'Star Comics'")
        return None
