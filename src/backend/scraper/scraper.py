import os
import requests
from bs4 import BeautifulSoup


class MangaRelease:
    """Represents a manga release."""
    
    def __init__(self, title: str, link: str, release_date: str, publisher: str):
        self.title = title
        self.link = link
        self.release_date = release_date
        self.publisher = publisher
    
    def __repr__(self):
        return f"MangaRelease(title={self.title}, link={self.link}, release_date={self.release_date}, publisher={self.publisher})"


class PublisherScraper:
    """Base class for scraping different manga publishers."""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    timeout = 5


    def __init__(self, manga: str, url: str):
        self.manga = manga
        self.url = url
    

    def scrape(self, params=None):
        """Scrapes the URL and returns the HTML response."""

        try:
            response = requests.get(self.url, headers=self.headers, params=params, timeout=self.timeout)
            if response.status_code == 200:
                return response.text
            
            else:
                print(f"Error: Received status code {response.status_code} while scraping {self.manga}")
                return None
            
        except requests.RequestException as e:
            print(f"Exception Error while fetching {self.manga}: {e}")
            return None


    def parse(self, response: str):
        """Abstract method for parsing the response; to be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement the 'parse' method.")


class PlanetMangaScraper(PublisherScraper):
    """Scraper for Planet Manga publisher."""

    def parse(self, response: str):
        if response is None:
            return None
        
        soup = BeautifulSoup(response, "html.parser")
        latest_item = soup.find("div", class_="product-item-info")
        
        if latest_item:
            title = latest_item.find("h3", class_="product-item-name").get_text(strip=True) if latest_item.find("h3") else ""
            link = latest_item.find("a", class_="product-item-link")["href"] if latest_item.find("a") else ""
            release_date = latest_item.find("div", class_="product-item-attribute-release-date").get_text(strip=True) if latest_item.find("div", class_="product-item-attribute-release-date") else ""
            
            return MangaRelease(title, link, release_date, "Planet Manga")
        
        print(f"Error: No results found for '{self.manga}' from 'Planet Manga'.")
        return None


class StarComicsScraper(PublisherScraper):
    """Scraper for Star Comics publisher."""

    base_url = "https://www.starcomics.com"
    
    def parse(self, response: str):
        if response is None:
            return None
        
        soup = BeautifulSoup(response, "html.parser")
        latest_item = soup.find("div", class_="fumetto-card")
        
        if latest_item:
            title = latest_item.find("h4", class_="card-title").get_text(strip=True) if latest_item.find("h4") else ""
            link = self.base_url + latest_item.find("a")["href"] if latest_item.find("a") else ""
            release_date = latest_item.find("p", class_="card-text").find("span", class_="text-secondary").get_text(strip=True) if latest_item.find("p").find("span") else ""
            
            return MangaRelease(title, link, release_date, "Star Comics")
        
        print(f"Error: No results found for '{self.manga}' from 'Star Comics'.")
        return None
    

    class MangaScraperApp:
        """Orchestrator class to manage scraping from multiple sources."""

        def __init__(self):
            #self.file_handler = FileHandler("./scraped_html/")
            self.scrapers = [
                PlanetMangaScraper("jujutsu kaisen", "https://www.panini.it/shp_ita_it/catalogsearch/result/?q=jujutsu+kaisen"),
                PlanetMangaScraper("chainsaw man", "https://www.panini.it/shp_ita_it/catalogsearch/result/?q=chainsaw+man"),
                StarComicsScraper("solo leveling", "https://www.starcomics.com/titoli-fumetti/solo-leveling")
            ]

        def scrape_and_notify(self):
            for scraper in self.scrapers:
                print(f"Scraping {scraper.manga}...")
                response = scraper.scrape(params={"q": scraper.manga} if isinstance(scraper, PlanetMangaScraper) else None)
                manga_release = scraper.parse(response)

                if manga_release:
                    print(f"Found release: {manga_release}")
                    #self.file_handler.save_response_to_file(scraper.manga, manga_release.publisher, response)



