import logging
import re

from datetime import datetime
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
                "Jujutsu Kaisen",
                "https://www.panini.it/shp_ita_it/catalogsearch/result/?q=jujutsu+kaisen"
            ),
            PlanetMangaScraper(
                "Chainsaw Man",
                "https://www.panini.it/shp_ita_it/catalogsearch/result/?q=chainsaw+man"
            ),
            StarComicsScraper(
                "Solo Leveling",
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
                self.insert_manga_release_db(scraper.manga, manga_release)

            else:
                logger.warning(f"No release found for {scraper.manga}")
        
        logger.info(f"Closing RDS connection...")
        self.db_connector.close()

        return


    def insert_manga_release_db(self, manga_title, manga_release):
        query = """
        INSERT INTO manga_releases (manga_title, volume_number, release_date, publisher, alert_sent)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (manga_title, volume_number, release_date) DO NOTHING;
        """

        release_date = self.parse_release_date(manga_release.release_date)
        volume_number = self.extract_volume_number(manga_release.title)

        query_params = [manga_title, volume_number, release_date, manga_release.publisher, False]

        try:
            self.db_connector.execute_query(query, query_params)
            logger.info("Inserted manga release: %s, release_date: %s\n", manga_release.title, manga_release.release_date)

        except Exception as e:
            logger.error("Failed to insert manga release: %s, error: %s\n", manga_release.title, e)


    def extract_volume_number(self, title):
        # This regex assumes the volume number is at the end of the title
        match = re.search(r'(\d+)$', title)
        if match:
            return match.group(1)
        else:
            return 'Unknown' 


    def parse_release_date(self, date_str):
        # Handle Multiple Date Formats
        for fmt in ('%d/%m/%Y', '%d/%m/%y'):
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Date format for '{date_str}' is not supported.")



