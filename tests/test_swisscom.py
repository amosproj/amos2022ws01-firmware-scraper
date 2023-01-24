import pytest
from selenium.common.exceptions import WebDriverException

from src.logger_old import create_logger_old
from src.Vendors import SwisscomScraper
from src.Vendors.swisscom.swisscom import DOWNLOAD_URL_EN


def test_entry_point_url_valid():
    scraper = SwisscomScraper(create_logger_old(), scrape_entry_url=DOWNLOAD_URL_EN)
    scraper.driver.get(scraper.scrape_entry_url)


def test_entry_point_url_invalid():
    with pytest.raises(WebDriverException):
        invalid_entry_point_url = "https://www.swisscom.chh"
        scraper = SwisscomScraper(create_logger_old(), scrape_entry_url=invalid_entry_point_url)
        scraper.driver.get(scraper.scrape_entry_url)


def test_scrape_product_metadata():
    scraper = SwisscomScraper(create_logger_old())
    scraped_data = scraper.scrape_metadata()
    for entry in scraped_data:
        assert entry["manufacturer"] == "Swisscom"
        assert entry["product_name"] is not None
        assert entry["product_type"] is not None
        assert entry["version"] is not None
        assert entry["download_link"] is not None
