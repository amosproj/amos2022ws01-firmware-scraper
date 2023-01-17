import pytest
from selenium.common.exceptions import WebDriverException

from src.logger import create_logger
from src.Vendors import ABBScraper
from src.Vendors.ABB.ABB import HOME_URL


def test_entry_point_url_valid():
    scraper = ABBScraper(create_logger(), scrape_entry_url=HOME_URL, headless=False)
    scraper.driver.get(scraper.vendor_url)


def test_entry_point_url_invalid():
    with pytest.raises(WebDriverException):
        invalid_entry_point_url = "https://library.abb.con/r?dkg=dkg_software&q=firmwarexx"
        scraper = ABBScraper(create_logger(), scrape_entry_url=invalid_entry_point_url, headless=False)
        scraper.driver.get(scraper.vendor_url)


def test_scrape_product_metadata():
    scraper = ABBScraper(create_logger(), headless=False, max_products=5)
    scraped_data = scraper.scrape_metadata()
    for entry in scraped_data:
        assert entry["manufacturer"] == "ABB"
        assert entry["product_name"] is not None
        assert entry["product_type"] is not None
        assert entry["download_link"] is not None