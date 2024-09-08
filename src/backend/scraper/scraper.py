import os
import json
import requests
from bs4 import BeautifulSoup


class Scraper():

    headers = { 
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36" 
    }
    timeout = 5
    manga_to_url_dictionary = {
        ("solo leveling", "star_comics") : "https://www.starcomics.com/titoli-fumetti/solo-leveling",
        ("jujutsu kaisen", "planet_manga") : "https://www.panini.it/shp_ita_it/catalogsearch/result/",
        ("chainsaw man" , "planet_manga") : "https://www.panini.it/shp_ita_it/catalogsearch/result/"
    }
    path_to_save_html = "./html_scraped/"

    def __init__(self) -> None:
        pass

    def scrape_and_parse_all(self):

        for (manga, publisher), url in self.manga_to_url_dictionary.items():

            print(f"Scraping {manga} from {publisher}...")

            if publisher == "planet_manga":
                response = self.scrape(manga, url, params = { "q" : manga })
                self.html_parse_planet_manga(response, manga, publisher)

            
            elif publisher == "star_comics": 
                response = self.scrape(manga, url)
                self.html_parse_star_comics(response, manga, publisher)



    def save_response_to_file(self, manga: str, publisher : str, response):
        filename = f"{manga.replace(' ', '_')}_{publisher}.txt"
        full_path = os.path.join(self.path_to_save_html, filename)

        os.makedirs(self.path_to_save_html, exist_ok=True)

        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(response)
            print(f"Saved response to {full_path}")

        except Exception as e:
            print(f"Error saving the file {full_path}: {e}")


    def scrape(self, manga: str, url: str, params=None):

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            
            # Check if the response is successful
            if response.status_code == 200:
                res_text = response.text
                return res_text
     
            else:
                print(f"Error: Received status code {response.status_code}")
                return None
    
        except requests.RequestException as e:
            print(f"Error while fetching {manga}: {e}")


    def html_parse_planet_manga(self, response, manga, publisher):

        soup = BeautifulSoup(response, "html.parser")
        self.save_response_to_file(manga, publisher, soup.prettify())

        # First item is the latest, Planet Manga automatically orders by decreasing release date
        latest_item = soup.find("div", class_="product-item-info")

        if latest_item:
            print(f"Found the latest item for '{manga}' from '{publisher}':")

            title_tag = latest_item.find("h3", class_="product-item-name")
            title = title_tag.get_text(strip=True) if title_tag else ""

            link_tag = latest_item.find("a", class_="product-item-link")
            link = link_tag["href"] if link_tag else ""

            release_date_tag = latest_item.find("div", class_="product-item-attribute-release-date")
            release_date = release_date_tag.get_text(strip=True) if release_date_tag else ""

            latest_manga = {
                "title": title,
                "link": link,
                "release_date": release_date
            }
            latest_manga_json = json.dumps(latest_manga, ensure_ascii=False, indent=4)
            print(latest_manga_json)

            return latest_manga_json

        else:
            print(f"No results found for '{manga}' from '{publisher}'.")
            return None


    def html_parse_star_comics(self, response, manga, publisher):

        soup = BeautifulSoup(response, "html.parser")
        self.save_response_to_file(manga, publisher, soup.prettify())

        # First item is the latest, Star Comics automatically orders by decreasing release date
        latest_item = soup.find("div", class_="fumetto-card")  

        if latest_item:
            print(f"Found the latest item for '{manga}' from '{publisher}':")

            title_tag = latest_item.find("h4", class_="card-title")  
            title = title_tag.get_text(strip=True) if title_tag else ""

            link_tag = latest_item.find("a") 
            link = "https://www.starcomics.com" + link_tag["href"] if link_tag else "" 

            release_date_tag = latest_item.find("p", class_="card-text").find("span", class_="text-secondary")
            release_date = release_date_tag.get_text(strip=True) if release_date_tag else ""

            latest_manga = {
                "title": title,
                "link": link,
                "release_date": release_date
            }
            latest_manga_json = json.dumps(latest_manga, ensure_ascii=False, indent=4)
            print(latest_manga_json)

            return latest_manga_json

        else:
            print(f"No results found for '{manga}' from '{publisher}'.")
            return None


def main():
    scraper = Scraper()
    scraper.scrape_and_parse_all()



if __name__ == "__main__":
    main()




