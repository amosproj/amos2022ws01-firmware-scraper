import pytest
from selenium.common.exceptions import WebDriverException

from src.logger_old import create_logger_old
from src.Vendors import TPLinkScraper
from src.Vendors.tp_link.tp_link import DOWNLOAD_URL_GLOBAL


def test_entry_point_url_valid():
    scraper = TPLinkScraper(create_logger_old(), scrape_entry_url=DOWNLOAD_URL_GLOBAL)
    scraper.driver.get(scraper.scrape_entry_url)


def test_entry_point_url_invalid():
    with pytest.raises(WebDriverException):
        invalid_entry_point_url = "https://www.tp-link.con"
        scraper = TPLinkScraper(create_logger_old(), scrape_entry_url=invalid_entry_point_url)
        scraper.driver.get(scraper.scrape_entry_url)


def test_scrape_product_metadata():
    scraper = TPLinkScraper(create_logger_old(), max_products=10)
    scraped_data = scraper.scrape_metadata()
    for entry in scraped_data:
        assert entry["manufacturer"] == "TP-Link"
        assert entry["product_name"] is not None
        assert entry["product_type"] is not None
        assert entry["version"] is not None
        assert entry["release_date"] is not None
        assert entry["download_link"] is not None
