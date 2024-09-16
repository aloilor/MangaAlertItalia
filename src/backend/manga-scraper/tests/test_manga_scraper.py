import pytest
import requests
import tempfile
import os
from unittest.mock import patch, mock_open, Mock
from scrapers.publisher_scraper import PublisherScraper
from scrapers.planet_manga_scraper import PlanetMangaScraper
from scrapers.star_comics_scraper import StarComicsScraper
from models.manga_release import MangaRelease
from utils.file_handler import FileHandler
from manga_scraper_app import MangaScraperApp

# Test data for mocking
planet_manga_valid_html = '''
    <li class="item product product-item">
        <div class="product-item-info" data-container="product-grid" id="product-item-info_244371">
            <!-- PNN labels -->
            <div class="product photo product-item-photo" tabindex="-1">
                <a class="product link product-item-link" href="https://www.panini.it/shp_ita_it/chainsaw-man-17-mmost027-it08.html">
                    <span class="product-image-container product-image-container-244371">
                        <span class="product-image-wrapper">
                            <img alt="Panini: Fumetti_Chainsaw Man 17" class="product-image-photo" height="222" loading="lazy" src="https://www.panini.it/media/catalog/product/cache/e60babe66e245861dcdd1290f02aaeda/M/M/MMOST027_0.jpg" width="222"/>
                        </span>
                    </span>
                    <style>
                        .product-image-container-244371 {
                            width: 222px;
                        }
                        .product-image-container-244371 span.product-image-wrapper {
                            padding-bottom: 100%;
                        }
                    </style>
                    <script type="text/javascript">
                        prodImageContainers = document.querySelectorAll(".product-image-container-244371");
                        for (var i = 0; i < prodImageContainers.length; i++) {
                            prodImageContainers[i].style.width = prodImageContainers[i].querySelector('.product-image-photo').getAttribute('width') + 'px';
                        }
                        prodImageContainersWrappers = document.querySelectorAll(".product-image-container-244371  span.product-image-wrapper");
                        for (var i = 0; i < prodImageContainersWrappers.length; i++) {
                            prodImageContainersWrappers[i].style.paddingBottom = "100%";
                        }
                    </script>
                </a>
                <div class="actions-secondary" data-role="add-to-links">
                    <a aria-label="Aggiungi alla lista desideri" class="action towishlist" data-action="add-to-wishlist" data-post='{"action":"https:\/\/www.panini.it\/shp_ita_it\/wishlist\/index\/add\/","data":{"product":244371,"uenc":"aHR0cHM6Ly93d3cucGFuaW5pLml0L3NocF9pdGFfaXQvY2F0YWxvZ3NlYXJjaC9yZXN1bHQvP3E9Y2hhaW5zYXcrbWFu"}}' href="#" role="button" title="Aggiungi alla lista desideri">
                        <span>Aggiungi alla lista desideri</span>
                    </a>
                </div>
            </div>
            <div class="product details product-item-details">
                <h3 class="product name product-item-name">
                    <a class="product-item-link" href="https://www.panini.it/shp_ita_it/chainsaw-man-17-mmost027-it08.html">Chainsaw Man 17</a>
                </h3>
                <!-- PNN attributes -->
                <div class="product attributes product-item-attributes">
                    <div class="product attribute typology product-item-attribute-typology">
                        <small>Fumetti</small>
                    </div>
                    <div class="product attribute type product-item-attribute-release-date">
                        <small>19/09/24</small>
                    </div>
                </div>
                <div class="price-box price-final_price" data-price-box="product-id-244371" data-product-id="244371" data-role="priceBox">
                    <span class="old-price">
                        <span class="price-container price-final_price tax weee">
                            <span class="price-label">Prezzo predefinito</span>
                            <span class="price-wrapper" data-price-amount="5.2" data-price-type="oldPrice" id="old-price-244371">
                                <span class="price">5,20 €</span>
                            </span>
                        </span>
                    </span>
                    <span class="discount-price">-5%</span>
                    <span class="special-price">
                        <span class="price-container price-final_price tax weee">
                            <span class="price-label">Prezzo speciale</span>
                            <span class="price-wrapper" data-price-amount="4.94" data-price-type="finalPrice" id="product-price-244371">
                                <span class="price">4,94 €</span>
                            </span>
                        </span>
                    </span>
                </div>
                <div class="product-item-inner">
                    <div class="product actions product-item-actions">
                        <div class="actions-primary">
                            <form action="https://www.panini.it/shp_ita_it/checkout/cart/add/uenc/aHR0cHM6Ly93d3cucGFuaW5pLml0L3NocF9pdGFfaXQvY2F0YWxvZ3NlYXJjaC9yZXN1bHQvP3E9Y2hhaW5zYXcrbWFu/product/244371/" data-product-sku="MMOST027_IT08" data-role="tocart-form" method="post">
                                <input name="product" type="hidden" value="244371"/>
                                <input name="uenc" type="hidden" value="aHR0cHM6Ly93d3cucGFuaW5pLml0L3NocF9pdGFfaXQvY2hlY2tvdXQvY2FydC9hZGQvdWVuYy9hSFIwY0hNNkx5OTNkM2N1Y0dGdWFXNXBMbWwwTDNOb2NGOXBkR0ZmYVhRdlkyRjBZV3h2WjNObFlYSmphQzl5WlhOMWJIUXZQM0U5WTJoaGFXNXpZWGNyYldGdS9wcm9kdWN0LzI0NDM3MS8,"/>
                                <input name="form_key" type="hidden" value="B2sGAQl6BNrpaSYY">
                                <input name="pnn_referral" type="hidden" value="">
                                <script>
                                    require(['campaignLocalStorage'], function (campaignLocalStorage) {
                                        campaignLocalStorage.campaignStorage("input[name='pnn_referral']", "MMOST027_IT08", "", "", {"_1679910884652_652":{"partner":"ticketone"}});
                                    });
                                </script>
                                <!-- PNN button -->
                                <div class="stock unavailable" title="Disponibilita'">
                                    <span>Non Disponibile</span>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </li>

'''

planet_manga_missing_html = '''
    <div class="product-item-info">
        <h3 class="product-item-name"></h3>
        <a class="product-item-link" href=""></a>
        <div class="product-item-attribute-release-date"></div>
    </div>
'''

star_comics_html = '''
    <div class="col-sm-6 col-lg-3 mb-4">
        <div class="card fumetto-card border-0">
            <a href="/fumetto/solo-leveling-18" title="SOLO LEVELING n. 18">
                <div class="card-img-top">
                    <figure class="mb-0">
                        <img alt="SOLO LEVELING n. 18" height="1679" loading="lazy" src="/files/immagini/fumetti-cover/thumbnail/sololeveling-18-1200px" title="SOLO LEVELING n. 18" width="1199"/>
                    </figure>
                </div>
            </a>
            <a href="/fumetto/solo-leveling-18" title="SOLO LEVELING n. 18">
                <div class="card-body text-center">
                    <h4 class="card-title mb-0">SOLO LEVELING n. 18</h4>
                    <p class="card-text mb-0 d-flex flex-column justify-content-end">
                        <span class="text-secondary">03/09/2024</span>
                    </p>
                </div>
            </a>
            <div class="text-center">
                <div class="d-flex justify-content-between m-auto nav-card-options">
                    <div class="d-flex align-items-center font-weight-bold ml-0">€ 9,90</div>
                    <div class="mr-0">
                        <div class="nav justify-content-end">
                            <div class="nav-item">
                                <a class="btn btn-link" href="/accedi?r=%2Ftitoli-fumetti%2Fsolo-leveling" rel="noindex nofollow" title="Aggiungi alla wishlist">
                                    <i class="far fa-heart"></i>
                                </a>
                            </div>
                            <div class="nav-item">
                                <a class="btn btn-link text-muted pr-0" rel="noindex nofollow" title="Fumetto non disponibile">
                                    <i class="fas fa-shopping-cart"></i>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
'''

star_comics_missing_html = '''
    <div class="fumetto-card">
        <h4 class="card-title"></h4>
        <a href=""></a>
        <p class="card-text"><span class="text-secondary"></span></p>
    </div>
'''

no_results_html = '''
<div class="no-products-found">No products available</div>
'''


class TestMangaRelease:

    def test_manga_release_repr(self):
        """Test that the __repr__ method returns the correct string."""

        title = "Attack on Titan Vol. 1"
        link = "https://example.com/attack-on-titan-vol-1"
        release_date = "2023-10-01"
        publisher = "Kodansha"
        
        manga = MangaRelease(title, link, release_date, publisher)
        
        expected_repr = (
            "MangaRelease(\n"
            " title: Attack on Titan Vol. 1,\n"
            " link: https://example.com/attack-on-titan-vol-1,\n"
            " release_date: 2023-10-01,\n"
            " publisher: Kodansha\n"
            ")\n"
        )
        
        assert repr(manga) == expected_repr


class TestFileHandler:

    def test_save_response_to_file_success(self):
        response = planet_manga_valid_html
        manga = "chainsaw man"
        publisher = "planet_manga"

        # Temporary files and directory to keep everything clean 
        with tempfile.TemporaryDirectory() as temp_dir:
            handler = FileHandler(temp_dir)
            handler.save_response_to_file(manga, publisher, response)

            expected_filename = f"{manga.replace(' ', '_')}_{publisher}.txt"
            expected_file_path = os.path.join(temp_dir, expected_filename)

            assert os.path.exists(expected_file_path) is not None

            with open(expected_file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
                assert file_content == response 
    
    def test_save_response_to_file_exception(self):
        response = planet_manga_valid_html
        manga = "chainsaw man"
        publisher = "planet_manga"
        path_to_save_html = "/fake/path"


        # Mock os.makedirs to prevent actual directory creation
        with patch("os.makedirs", return_value=True):
            handler = FileHandler(path_to_save_html)

            # Simulate an IOError when attempting to open the file
            with patch("builtins.open", mock_open()) as mock_file:
                mock_file.side_effect = IOError("File write error")
            
                with patch("utils.file_handler.logger") as mock_logger:
                    handler.save_response_to_file(manga, publisher, response)

                    mock_logger.error.assert_called_with(
                        f"Error saving file /fake/path/chainsaw_man_planet_manga.txt: File write error"
                    )

class TestPublisherScraper:

    @pytest.fixture
    def scraper(self):
        manga = "chainsaw man"
        url = "https://www.panini.it/shp_ita_it/catalogsearch/result/"
        return PublisherScraper(manga, url)

    def test_scrape_success(self, scraper, requests_mock):
        params = {"q": "chainsaw man"}
        requests_mock.get(scraper.url, text=planet_manga_valid_html)
        response = scraper.scrape(params)

        assert response is not None
        assert response == planet_manga_valid_html

    def test_scrape_non_200_status(self, scraper, requests_mock):
        params = {"q": "chainsaw man"}
        requests_mock.get(scraper.url, status_code=404)
        response = scraper.scrape(params)

        assert response is None

    def test_scrape_exception(self, scraper, requests_mock):
        params = {"q": "chainsaw man"}

        requests_mock.get(scraper.url, exc=requests.exceptions.ConnectTimeout)
        response = scraper.scrape(params)

        assert response is None


class TestPlanetMangaScraper:

    @pytest.fixture
    def scraper(self):
        manga = "chainsaw man"
        url = "https://www.panini.it/shp_ita_it/catalogsearch/result/"
        return PlanetMangaScraper(manga, url)

    def test_parse_valid_response(self, scraper):
        """Test parse method with valid HTML content"""
        scraper.scrape = Mock(return_value=planet_manga_valid_html)
        
        response = scraper.scrape()
        result = scraper.parse(response)

        expected_release = MangaRelease(
            title = "Chainsaw Man 17",
            link = "https://www.panini.it/shp_ita_it/chainsaw-man-17-mmost027-it08.html",
            release_date = "19/09/24",
            publisher = "planet_manga"
        )

        assert result is not None
        assert isinstance(result, MangaRelease)
        assert result.title == expected_release.title
        assert result.link == expected_release.link
        assert result.release_date == expected_release.release_date
        assert result.publisher == expected_release.publisher
    
    def test_parse_none_response(self, scraper, capsys):
        """Test parse method with None HTML content"""
        scraper.scrape = Mock(return_value=None)
        
        with patch("scrapers.planet_manga_scraper.logger") as mock_logger:
            response = scraper.scrape()
            result = scraper.parse(response)            
            mock_logger.error.assert_called_with(
                f"No response for '{scraper.manga}' from 'Planet Manga'"
            )
        
        assert result is None

    
    def test_parse_no_results(self, scraper, capsys):
        """Test parse method when no product item is found"""
        scraper.scrape = Mock(return_value=no_results_html)
        
        with patch("scrapers.planet_manga_scraper.logger") as mock_logger:
            response = scraper.scrape()
            result = scraper.parse(response)
            mock_logger.error.assert_called_with(
                f"No results found for '{scraper.manga}' from 'Planet Manga'"
            )
        
        assert result is None

    
    def test_parse_missing_elements(self, scraper):
        """Test parse method with missing title, link, and release date"""
        scraper.scrape = Mock(return_value=planet_manga_missing_html)

        with patch("scrapers.planet_manga_scraper.logger") as mock_logger:
            response = scraper.scrape()
            result = scraper.parse(response)
            mock_logger.error.assert_called_with(
                f"Missing data in response for '{scraper.manga}' from 'Planet Manga'"
            )
        
        assert result is None


class TestStarComicsScraper:

    @pytest.fixture
    def scraper(self):
        manga = "solo leveling"
        url = "https://www.starcomics.com/titoli-fumetti/solo-leveling"
        return StarComicsScraper(manga, url)
    
    def test_parse_valid_response(self, scraper):
        """Test parse method with valid HTML content"""
        scraper.scrape = Mock(return_value=star_comics_html)
        
        response = scraper.scrape()
        result = scraper.parse(response)

        expected_release = MangaRelease(
            title = "SOLO LEVELING n. 18",
            link = "https://www.starcomics.com/fumetto/solo-leveling-18",
            release_date = "03/09/2024",
            publisher = "star_comics"
        )

        assert result is not None
        assert isinstance(result, MangaRelease)
        assert result.title == expected_release.title
        assert result.link == expected_release.link
        assert result.release_date == expected_release.release_date
        assert result.publisher == expected_release.publisher

    def test_parse_none_response(self, scraper, capsys):
        """Test parse method with None HTML content"""
        scraper.scrape = Mock(return_value=None)
        
        with patch("scrapers.star_comics_scraper.logger") as mock_logger:
            response = scraper.scrape()
            result = scraper.parse(response)            
            mock_logger.error.assert_called_with(
                f"No response for '{scraper.manga}' from 'Star Comics'"
            )

        assert result is None


    def test_parse_no_results(self, scraper, capsys):
        """Test parse method when no product item is found"""
        scraper.scrape = Mock(return_value=no_results_html)
        
        with patch("scrapers.star_comics_scraper.logger") as mock_logger:
            response = scraper.scrape()
            result = scraper.parse(response)
            mock_logger.error.assert_called_with(
                f"No results found for '{scraper.manga}' from 'Star Comics'"
            )
        assert result is None


    def test_parse_missing_elements(self, scraper):
        """Test parse method with missing title, link, and release date"""
        scraper.scrape = Mock(return_value=planet_manga_missing_html)

        response = scraper.scrape()
        result = scraper.parse(response)

        assert result is None
    


