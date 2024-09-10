import pytest
import requests
import tempfile
import os
from unittest.mock import patch, mock_open
from bs4 import BeautifulSoup
from ..scraper_old import Scraper


# Test data for mocking
planet_manga_html = '''
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

invalid_html = '''
<div class="no-products-found">No products available</div>
'''



@pytest.fixture
def scraper():
    return Scraper() 


def test_can_scrape_planet_manga(scraper, requests_mock):
    url = "https://www.panini.it/shp_ita_it/catalogsearch/result/"
    params = {"q": "chainsaw man"}
    requests_mock.get(url, text=planet_manga_html)
    
    response = scraper.scrape("chainsaw man", url, params=params)

    assert response is not None
    assert response == planet_manga_html


def test_can_scrape_star_comics(scraper, requests_mock):
    url = "https://www.starcomics.com/titoli-fumetti/solo-leveling"
    requests_mock.get(url, text=star_comics_html)

    response = scraper.scrape("solo leveling", url)

    assert response is not None
    assert response == star_comics_html


def test_scrape_error_handling(scraper, requests_mock):
    url = "https://www.panini.it/shp_ita_it/catalogsearch/result/"
    params = {"q": "chainsaw man"}
    requests_mock.get(url, status_code=404)
    
    response = scraper.scrape("chainsaw man", url, params=params)
    
    assert response is None


def test_scrape_exception_handling(scraper, requests_mock, capsys):
    url = "https://www.panini.it/shp_ita_it/catalogsearch/result/"
    params = {"q": "chainsaw man"}

    requests_mock.get(url, exc=requests.exceptions.ConnectTimeout)
    response = scraper.scrape("chainsaw man", url, params=params)

    assert response is None
    
    # Verify print statement for logging the exception message
    captured = capsys.readouterr()
    assert "Exception Error while fetching" in captured.out


def test_html_parse_planet_manga(scraper):
    response = planet_manga_html
    result = scraper.html_parse_planet_manga(response, "chainsaw man", "planet_manga")

    assert result is not None
    assert result['title'] == "Chainsaw Man 17"
    assert result['link'] == "https://www.panini.it/shp_ita_it/chainsaw-man-17-mmost027-it08.html"
    assert result['release_date'] == "19/09/24"
    assert result['publisher'] == "planet_manga"


def test_html_parse_solo_leveling(scraper):
    response = star_comics_html
    result = scraper.html_parse_star_comics(response, "solo leveling", "star_comics")

    assert result is not None
    assert result['title'] == "SOLO LEVELING n. 18"
    assert result['link']  == "https://www.starcomics.com/fumetto/solo-leveling-18" 
    assert result['release_date'] == "03/09/2024"
    assert result['publisher'] == "star_comics"


def test_html_parse_planet_manga_error_handling_invalid_html(scraper):
    response = invalid_html
    result = scraper.html_parse_planet_manga(response, "chainsaw man", "planet_manga")
    
    assert result is None


def test_html_parse_planet_manga_error_handling_none_response(scraper):
    response = None
    result = scraper.html_parse_planet_manga(response, "chainsaw man", "planet_manga")
    
    assert result is None


def test_html_parse_star_comics_error_handling_invalid_html(scraper):
    response = invalid_html
    result = scraper.html_parse_star_comics(response, "solo leveling", "star_comics")
    
    assert result is None


def test_html_parse_star_comics_error_handling_none_response(scraper):
    response = None
    result = scraper.html_parse_planet_manga(response, "solo leveling", "star_comics")
    
    assert result is None


def test_save_response_to_file(scraper):
    response = planet_manga_html
    manga = "chainsaw man"
    publisher = "planet_manga"

    # Temporary files and directory to keep everything clean 
    with tempfile.TemporaryDirectory() as temp_dir:

        scraper.path_to_save_html = temp_dir
        scraper.save_response_to_file("chainsaw man", "planet_manga", response)

        expected_filename = f"{manga.replace(' ', '_')}_{publisher}.txt"
        expected_file_path = os.path.join(temp_dir, expected_filename)

        assert os.path.exists(expected_file_path) is not None

        with open(expected_file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
            assert file_content == response 


def test_save_response_to_file_exception_handling(scraper):
    response = planet_manga_html
    manga = "chainsaw man"
    publisher = "planet_manga"

    scraper.path_to_save_html = "/fake/path"

    # Mock os.makedirs to prevent actual directory creation
    with patch("os.makedirs", return_value=True):
        
        # Simulate an IOError when attempting to open the file
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = IOError("File write error")
        
            with patch("builtins.print") as mock_print:
                scraper.save_response_to_file(manga, publisher, response)

                # Check if the error message was printed
                mock_print.assert_called_with(f"Error saving the file /fake/path/chainsaw_man_planet_manga.txt: File write error")






