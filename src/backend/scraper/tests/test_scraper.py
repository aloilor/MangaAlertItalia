import pytest
import requests
from unittest.mock import patch, mock_open
from bs4 import BeautifulSoup
from ..scraper import Scraper


# Test data for mocking
planet_manga_html = '''
    <div class="product details product-item-details">
        <h3 class="product name product-item-name">
            <a class="product-item-link" href="https://www.panini.it/shp_ita_it/chainsaw-man-16-mmost026-it08.html">
                Chainsaw Man 16
            </a>
        </h3>
        <!-- PNN attributes -->
        <div class="product attributes product-item-attributes">
            <div class="product attribute typology product-item-attribute-typology">
                <small>Fumetti</small>
            </div>
            <div class="product attribute type product-item-attribute-release-date">
                <small>09/05/24</small>
            </div>
        </div>
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
    assert "Chainsaw Man 16" in response
    assert "https://www.panini.it/shp_ita_it/chainsaw-man-16-mmost026-it08.html" in response
    assert "09/05/24" in response

def test_can_scrape_star_comics(scraper, requests_mock):
    url = "https://www.starcomics.com/titoli-fumetti/solo-leveling"
    requests_mock.get(url, text=star_comics_html)

    response = scraper.scrape("solo leveling", url)

    assert response is not None
    assert response == star_comics_html
    assert "SOLO LEVELING n. 18" in response
    assert "/fumetto/solo-leveling-18" in response
    assert "03/09/2024" in response



