import random

import pytest
from selenium.common.exceptions import WebDriverException

from logger import create_logger
from Vendors import SchneiderElectricScraper
from Vendors.schneider_electric.schneider_electric import DOWNLOAD_URL_GLOBAL


def test_entry_point_url_valid():
    scraper = SchneiderElectricScraper(
        create_logger(), scrape_entry_url=DOWNLOAD_URL_GLOBAL)
    scraper.driver.get(scraper.scrape_entry_url)


def test_entry_point_url_invalid():
    with pytest.raises(WebDriverException):
        invalid_entry_point_url = "https://www.se.con"
        scraper = SchneiderElectricScraper(
            create_logger(), scrape_entry_url=invalid_entry_point_url)
        scraper.driver.get(scraper.scrape_entry_url)


def test_scrape_product_page_urls():
    scraper = SchneiderElectricScraper(create_logger(), max_products=20)
    product_page_urls = scraper._scrape_product_page_urls()
    assert len(product_page_urls) == 20
    assert all(["se.com" in url for url in product_page_urls])


def test_scrape_product_metadata():
    scraper = SchneiderElectricScraper(create_logger(), max_products=20)
    product_page_urls = scraper._scrape_product_page_urls()
    for _ in range(3):
        url = random.choice(product_page_urls)
        metadata_list = scraper._scrape_product_metadata(url)
        for entry in metadata_list:
            assert entry["manufacturer"] == "SchneiderElectric"
            assert entry["product_name"] is not None
            assert entry["product_type"] is not None
            assert entry["version"] is not None
            assert entry["release_date"] is not None
            assert "download.schneider-electric.com" in entry["download_link"]
