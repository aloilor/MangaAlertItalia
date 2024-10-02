from utils.logging_config import setup_logging
from manga_scraper_app import MangaScraperApp
import logging

logger = logging.getLogger(__name__)


def main():
    setup_logging()
    logger.info(f"Starting to scrape...")
    app = MangaScraperApp()
    app.scrape_and_notify()
    logger.info(f"Scrape ended...")

if __name__ == "__main__":
    main()



