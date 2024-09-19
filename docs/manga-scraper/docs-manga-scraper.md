# Manga Scraper

## Directory Structure

```
manga_scraper/  
├── Dockerfile                      # Instructions to build the Docker image for the application.
├── build_requirements.txt          # Dependencies required to build the application (non-test-related).
├── main.py                         # Entry point for the application that triggers the scraping process.
├── manga_scraper_app.py            # Contains the `MangaScraperApp` class, orchestrating the scraping and notification process.
├── models/  
│   ├── __init__.py                 
│   └── manga_release.py            # Defines the `MangaRelease` class, representing the scraped manga release data.
├── scrapers/  
│   ├── __init__.py                 
│   ├── publisher_scraper.py        # Base class `PublisherScraper` for scraping manga publishers' websites.
│   ├── planet_manga_scraper.py     # Scraper implementation for the Planet Manga publisher.
│   └── star_comics_scraper.py      # Scraper implementation for the Star Comics publisher.
├── tests/  
│   ├── __init__.py                 
│   ├── test_manga_scraper.py       # Test cases for the scraping functionality and related components.
│   ├── tests_requirements.txt      # Dependencies required to run the tests.
└── utils/  
    ├── __init__.py                 
    └── file_handler.py             # Defines `FileHandler` class for saving responses and handling file operations.
    └── logging_config.py           # Configures logging for the application.

```
