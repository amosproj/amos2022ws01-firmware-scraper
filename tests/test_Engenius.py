import pytest
from selenium.common.exceptions import WebDriverException

from src.logger import create_logger
from src.Vendors import EngeniusScraper
from src.Vendors.Engenius.Engenius import HOME_URL


def test_entry_point_url_valid():
    scraper = EngeniusScraper(
        create_logger(), scrape_entry_url=HOME_URL, headless=True)
    scraper.driver.get(scraper.scrape_entry_url)


def test_entry_point_url_invalid():
    with pytest.raises(WebDriverException):
        invalid_entry_point_url = "https://www.engeniusnetworks.e/downloads/"
        scraper = EngeniusScraper(
            create_logger(), scrape_entry_url=invalid_entry_point_url, headless=True)
        scraper.driver.get(scraper.scrape_entry_url)


def test_scrape_product_metadata():
    scraper = EngeniusScraper(create_logger(), headless=True, max_products=5)
    scraped_data = scraper.scrape_metadata()
    for entry in scraped_data:
        assert entry["manufacturer"] == "Engenius"
        assert entry["product_name"] is not None
        assert entry["product_type"] is not None
        assert entry["download_link"] is not None
