import logging
from scrapers.planet_manga_scraper import PlanetMangaScraper
from scrapers.star_comics_scraper import StarComicsScraper
from utils.file_handler import FileHandler

logger = logging.getLogger(__name__)

class MangaScraperApp:
    """Orchestrator class to manage scraping from multiple sources"""

    def __init__(self):
        #self.file_handler = FileHandler("./scraped_html/")

        self.scrapers = [
            PlanetMangaScraper(
                "jujutsu kaisen",
                "https://www.panini.it/shp_ita_it/catalogsearch/result/?q=jujutsu+kaisen"
            ),
            PlanetMangaScraper(
                "chainsaw man",
                "https://www.panini.it/shp_ita_it/catalogsearch/result/?q=chainsaw+man"
            ),
            StarComicsScraper(
                "solo leveling",
                "https://www.starcomics.com/titoli-fumetti/solo-leveling"
            )
        ]

    def scrape_and_notify(self):
        for scraper in self.scrapers:
            logger.info(f"Scraping {scraper.manga}...")
            params = {"q": scraper.manga} if isinstance(scraper, PlanetMangaScraper) else None
            response = scraper.scrape(params)
            manga_release = scraper.parse(response)

            if manga_release:
                logger.info(f"Found release: {manga_release}")
                #self.file_handler.save_response_to_file(scraper.manga, manga_release.publisher, response)
            else:
                logger.warning(f"No release found for {scraper.manga}")
