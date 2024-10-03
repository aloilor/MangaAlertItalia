import logging

from manga_scraper.scrapers.planet_manga_scraper import PlanetMangaScraper
from manga_scraper.scrapers.star_comics_scraper import StarComicsScraper
from manga_scraper.utils.file_handler import FileHandler

from aws_utils.db_connector import DatabaseConnector

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

        self.secret_name = "rds!db-4a66914f-6981-4530-b0ee-679115c8aa8a"

        self.db_connector = DatabaseConnector(self.secret_name)
        

    def scrape_and_notify(self):

        logger.info(f"Issuing RDS connection using secret {self.secret_name}...")
        self.db_connector.connect()

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
        
        logger.info(f"Closing RDS connection...")
        self.db_connector.close()

        return

