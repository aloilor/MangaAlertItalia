from utils.logging_config import setup_logging
from manga_scraper_app import MangaScraperApp

def main():
    setup_logging()
    app = MangaScraperApp()
    app.scrape_and_notify()

if __name__ == "__main__":
    main()
