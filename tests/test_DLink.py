import pytest
from selenium.common.exceptions import WebDriverException

from src.logger_old import create_logger_old
from src.Vendors import DLinkScraper
from src.Vendors.DLink.DLink import HOME_URL


def test_entry_point_url_valid():
    scraper = DLinkScraper(create_logger_old(), scrape_entry_url=HOME_URL, headless=True)
    scraper.driver.get(scraper.scrape_entry_url)


def test_entry_point_url_invalid():
    with pytest.raises(WebDriverException):
        invalid_entry_point_url = "https://tsd.dlink.con.tw"
        scraper = DLinkScraper(create_logger_old(), scrape_entry_url=invalid_entry_point_url, headless=True)
        scraper.driver.get(scraper.scrape_entry_url)


def test_scrape_product_metadata():
    scraper = DLinkScraper(create_logger_old(), headless=True, max_products=1)
    scraped_data = scraper.scrape_metadata()
    for entry in scraped_data:
        assert entry["manufacturer"] == "DLink"
        assert entry["product_name"] is not None
        assert entry["product_type"] is not None
        assert entry["download_link"] is not None
