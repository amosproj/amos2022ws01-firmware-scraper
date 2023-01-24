import pytest
from selenium.common.exceptions import WebDriverException

from src.logger_old import create_logger_old
from src.Vendors import QnapScraper
from src.Vendors.Qnap.Qnap import HOME_URL


def test_entry_point_url_valid():
    scraper = QnapScraper(create_logger_old(), scrape_entry_url=HOME_URL, headless=True)
    scraper.driver.get(scraper.scrape_entry_url)


def test_entry_point_url_invalid():
    with pytest.raises(WebDriverException):
        invalid_entry_point_url = "https://www.qnap.con/en/download?model=qutscloud&category=firmware"
        scraper = QnapScraper(create_logger_old(), scrape_entry_url=invalid_entry_point_url, headless=True)
        scraper.driver.get(scraper.scrape_entry_url)


def test_scrape_product_metadata():
    scraper = QnapScraper(create_logger_old(), headless=True, max_products=2)
    scraped_data = scraper.scrape_metadata()
    for entry in scraped_data:
        assert entry["manufacturer"] == "Qnap"
        assert entry["product_name"] is not None
        assert entry["product_type"] is not None
        assert entry["download_link"] is not None
