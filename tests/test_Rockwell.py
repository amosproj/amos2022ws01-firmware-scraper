import pytest
from selenium.common.exceptions import WebDriverException

from src.logger_old import create_logger_old
from src.Vendors import RockwellScraper


def test_connection_and_login():
    RWS = RockwellScraper(create_logger_old())
    RWS.login()


def test_scrape_product_metadata():
    RWS = RockwellScraper(create_logger_old(), max_products=5)
    scraped_data = RWS.scrape_metadata()
    for entry in scraped_data:
        assert entry["manufacturer"] == "Rockwell"
        assert entry["product_name"] is not None
        assert entry["product_type"] is not None
        assert entry["version"] is not None
        assert entry["download_link"] is not None
