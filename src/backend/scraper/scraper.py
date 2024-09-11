import os
import requests
from bs4 import BeautifulSoup


class MangaRelease:
    """Represents a manga release"""
    
    def __init__(self, title: str, link: str, release_date: str, publisher: str):
        self.title = title
        self.link = link
        self.release_date = release_date
        self.publisher = publisher
    
    def __repr__(self):
        return f"MangaRelease(\n title: {self.title},\n link: {self.link},\n release_date: {self.release_date},\n publisher: {self.publisher}\n)\n"


class FileHandler:
    """Handles file saving functionality for scraped data"""
    
    def __init__(self, path_to_save_html):
        self.path_to_save_html = path_to_save_html
        os.makedirs(self.path_to_save_html, exist_ok=True)
    
    def save_response_to_file(self, manga: str, publisher: str, response: str):
        filename = f"{manga.replace(' ', '_')}_{publisher}.txt"
        full_path = os.path.join(self.path_to_save_html, filename)

        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(response)
            print(f"Saved response to {full_path}")
        except Exception as e:
            print(f"Error saving the file {full_path}: {e}")


class PublisherScraper:
    """Base class for scraping different manga publishers websites"""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    timeout = 5

    def __init__(self, manga: str, url: str):
        self.manga = manga
        self.url = url
    
    def scrape(self, params=None):
        """Scrapes the URL and returns the HTML response"""

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
        """Abstract method for parsing the response; to be implemented by Scraper subclasses."""
        raise NotImplementedError("Subclasses must implement the 'parse' method.")


class PlanetMangaScraper(PublisherScraper):
    """Scraper for Planet Manga publisher"""

    def parse(self, response: str):
        if response is None:
            return None
        
        soup = BeautifulSoup(response, "html.parser")
        latest_item = soup.find("div", class_="product-item-info")
        
        if latest_item:
            title = latest_item.find("h3", class_="product-item-name").get_text(strip=True) if latest_item.find("h3", class_="product-item-name") else ""
            link = latest_item.find("a", class_="product-item-link")["href"] if latest_item.find("a", class_="product-item-link")["href"] else ""
            release_date = latest_item.find("div", class_="product-item-attribute-release-date").get_text(strip=True) if latest_item.find("div", class_="product-item-attribute-release-date") else ""
            
            # Return None if one of title, link and release_date is empty
            return MangaRelease(title, link, release_date, "planet_manga") if title and link and release_date else None
        
        print(f"Error: No results found for '{self.manga}' from 'Planet Manga'.")
        return None


class StarComicsScraper(PublisherScraper):
    """Scraper for Star Comics publisher"""

    base_url = "https://www.starcomics.com"
    
    def parse(self, response: str):
        if response is None:
            return None
        
        soup = BeautifulSoup(response, "html.parser")
        latest_item = soup.find("div", class_="fumetto-card")
        
        if latest_item:
            title = latest_item.find("h4", class_="card-title").get_text(strip=True) if latest_item.find("h4", class_="card-title") else ""
            link = self.base_url + latest_item.find("a")["href"] if latest_item.find("a")["href"] else ""
            release_date = latest_item.find("p", class_="card-text").find("span", class_="text-secondary").get_text(strip=True) if latest_item.find("p", class_="card-text").find("span", class_="text-secondary") else ""
            
            return MangaRelease(title, link, release_date, "planet_manga")
        
        print(f"Error: No results found for '{self.manga}' from 'Star Comics'.")
        return None
    

class MangaScraperApp:
    """Orchestrator class to manage scraping from multiple sources"""

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
            params = {"q": scraper.manga} if isinstance(scraper, PlanetMangaScraper) else None            
            response = scraper.scrape(params)
            manga_release = scraper.parse(response)

            if manga_release:
                print(f"Found release: {manga_release}")
                #self.file_handler.save_response_to_file(scraper.manga, manga_release.publisher, response)


def main():
    app = MangaScraperApp()
    app.scrape_and_notify()


if __name__ == "__main__":
    main()

