# Scraper documentation
The Manga Scraper module is designed to scrape manga release data from different publishers and platforms. It is modular, enabling easy extension to include new publishers or platforms. The application is structured into scrapers, models, utilities, and tests, making it a scalable and maintainable project.

## Directory Structure
```
manga_scraper/  
├── main.py                         # Entry point for the application that triggers the scraping process.
├── manga_scraper_app.py            # Contains the `MangaScraperApp` class, orchestrating the scraping and notification process.
├── requirements.txt                # Dependencies for the scraper application.
│
├── models/                         # Defines models used in the application      
│   └── manga_release.py            # Defines the `MangaRelease` class, representing the scraped manga release data.
│
├── scrapers/                       # Contains individual scrapers for each platform/publisher   
│   ├── publisher_scraper.py        # Base class `PublisherScraper` for scraping manga publishers' websites.
│   ├── planet_manga_scraper.py     # Scraper implementation for the Planet Manga publisher.
│   └── star_comics_scraper.py      # Scraper implementation for the Star Comics publisher.
│ 
└── utils/                          # Contains utility functions like logging and file handling
    └── file_handler.py             # Defines `FileHandler` class for saving responses and handling file operations.
    └── logging_config.py           # Configures logging for the application.
```

## Modules description 
### a. ```scrapers/```
This directory contains individual scrapers for different manga publishers or platforms. Each scraper is responsible for fetching data from its respective source. Currently, the following scrapers are available:
- planet_manga_scraper.py: Scrapes data from Planet Manga.
- star_comics_scraper.py: Scrapes data from Star Comics.
- publisher_scraper.py: Base class for creating new scrapers.

Each scraper should inherit from publisher_scraper.py, which provides a template to standardize scraping.

### b. ```models/```
- manga_release.py: Defines the data model used to represent a manga release. It includes fields like title, release date, and publisher

### c. ```utils/```
- file_handler.py: Handles file-related operations such as saving scraped data to disk.
- logging_config.py: Configures the logging system to track and log the application’s runtime information, useful for debugging.

### d. ```main.py```
This is the main entry point of the application. It initializes the scrapers and orchestrates the scraping process, saving the output in a structured format.

## Adding new scrapers 
To extend the scraper functionality to additional publishers, follow these steps:

1. Create a new file in the ```scrapers/``` directory, e.g., new_publisher_scraper.py.
2. Inherit from PublisherScraper defined in ```publisher_scraper.py```.
3. Implement the required methods, such as fetch_releases().

For example:
```python
from scrapers.publisher_scraper import PublisherScraper

class NewPublisherScraper(PublisherScraper):
    def fetch_releases(self):
        # Logic to scrape the new publisher's site
        pass
```

## Testing 
The project includes a test suite to ensure functionality. Tests are located in the ```tests/``` directory. To run the tests, install the required testing dependencies and use pytest.

```bash
pip install -r tests/tests_requirements.txt
pytest
```
This will run all unit tests, ensuring that the scrapers and other modules work as expected.

## Setup instructions 
Before running the application, ensure that your environment is properly set up.

### a. Dependencies
- Ensure that Python 3.8+ is installed on your machine.
- Install the required dependencies using build_requirements.txt:
```bash
pip install -r build_requirements.txt
```

### b. Running the application 
To run the manga scraper, execute the main script:
```python
python main.py
```

## Deployment with Docker
The project includes a Dockerfile for easy deployment. The Dockerfile installs dependencies and sets up the environment for the application to run in a container.

- Building the Image: 
```bash
docker build -t manga-scraper .
```

- Running the container: 
```bash
docker run manga-scraper
```

By using Docker, you can run the manga scraper on any system without worrying about dependencies.



