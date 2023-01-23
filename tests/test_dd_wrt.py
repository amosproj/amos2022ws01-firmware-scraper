import pytest
from selenium.common.exceptions import WebDriverException

from src.logger import create_logger
from src.Vendors import DDWRTScraper
from src.Vendors.dd_wrt.dd_wrt import DOWNLOAD_URL


def test_entry_point_url_valid():
    scraper = DDWRTScraper(create_logger(), scrape_entry_url=DOWNLOAD_URL)
    scraper.driver.get(scraper.scrape_entry_url)


def test_entry_point_url_invalid():
    with pytest.raises(WebDriverException):
        invalid_entry_point_url = "https://www.dd-wrt.con"
        scraper = DDWRTScraper(create_logger(), scrape_entry_url=invalid_entry_point_url)
        scraper.driver.get(scraper.scrape_entry_url)


def test_scrape_product_metadata():
    scraper = DDWRTScraper(create_logger(), max_products=10)
    scraped_data = scraper.scrape_metadata()
    for entry in scraped_data:
        assert entry["manufacturer"] == "DD-WRT"
        assert entry["product_name"] is not None
        assert entry["product_type"] is not None
        assert entry["release_date"] is not None
        assert entry["download_link"] is not None
