import pytest
from selenium.common.exceptions import WebDriverException

from src.logger import create_logger
from src.Vendors import BelkinScraper

logger = create_logger()


def test_init():
    Belkin = BelkinScraper(logger=logger)
    assert Belkin.name == "Belkin"
    assert Belkin.driver


def test_connection():
    with pytest.raises(WebDriverException):
        Belkin = BelkinScraper(logger=logger)
        Belkin.url = "download"
        Belkin.connect_webdriver()


def test_scraping():
    Belkin = BelkinScraper(logger=logger, max_products=1)
    Belkin.scrape_metadata()
    assert len(Belkin.catalog) >= 1
