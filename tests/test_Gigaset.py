import pytest
from selenium.common.exceptions import WebDriverException

from src.logger import create_logger
from src.Vendors import GigasetScraper

logger = create_logger()


def test_init():
    Gigaset = GigasetScraper(logger=logger)
    assert Gigaset.driver


def test_connection():
    with pytest.raises(WebDriverException):
        Gigaset = GigasetScraper(logger=logger)
        Gigaset.url = "download"
        Gigaset.connect_webdriver()


def test_scraping():
    Gigaset = GigasetScraper(logger=logger, max_products=1)
    Gigaset.scrape_metadata()
    assert len(Gigaset.catalog) >= 1
