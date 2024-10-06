from .publisher_scraper import PublisherScraper
from manga_scraper.models.manga_release import MangaRelease
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class PlanetMangaScraper(PublisherScraper):
    """Scraper for Planet Manga publisher"""

    def parse(self, response: str):
        if response is None:
            logger.error(f"No response for '{self.manga}' from 'Planet Manga'")
            return None

        soup = BeautifulSoup(response, "html.parser")
        latest_item = soup.find("div", class_="product-item-info")

        if latest_item:
            title_elem = latest_item.find("h3", class_="product-item-name")
            link_elem = latest_item.find("a", class_="product-item-link")
            date_elem = latest_item.find("div", class_="product-item-attribute-release-date")

            title = title_elem.get_text(strip=True) if title_elem else ""
            link = link_elem["href"] if link_elem and link_elem.get("href") else ""
            release_date = date_elem.get_text(strip=True) if date_elem else ""

            if title and link and release_date:
                return MangaRelease(title, link, release_date, "planet manga")
            else:
                logger.error(f"Missing data in response for '{self.manga}' from 'Planet Manga'")
                return None

        logger.error(f"No results found for '{self.manga}' from 'Planet Manga'")
        return None
