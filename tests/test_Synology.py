"""def test_init(Synology):
    assert Synology.url == "https://www.synology.com/en-global/support/download/"
    assert Synology.driver
    return Synology
"""

import pytest
from selenium.common.exceptions import WebDriverException

from src.logger import create_logger
from src.Vendors import SynologyScraper
#from src.Vendors.synology.synology import VENDOR_URL


def test_entry_point_url_valid():
    scraper = SynologyScraper(logger=create_logger())
    print(scraper.url)
    scraper.driver.get(scraper.url)


def test_entry_point_url_invalid():
    with pytest.raises(WebDriverException):
        invalid_entry_point_url = "https://www.dd-wrt.con"
        scraper = SynologyScraper(
            create_logger(), url=invalid_entry_point_url)
        scraper.driver.get(scraper.url)


def test_scrape_product_metadata():
    scraper = SynologyScraper(create_logger(), max_products=10)
    scraped_data = scraper.scrape_metadata()
    for entry in scraped_data:
        assert entry["manufacturer"] == "Synology"
        assert entry["product_name"] is not None
        assert entry["product_type"] is not None
        assert entry["release_date"] is not None
        assert entry["download_link"] is not None
