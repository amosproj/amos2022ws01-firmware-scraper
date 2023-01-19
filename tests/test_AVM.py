import pytest
from selenium.common.exceptions import WebDriverException

from src.logger import create_logger
from src.Vendors import AVMScraper

logger = create_logger()


def test_init():
    AVM = AVMScraper(logger=logger)
    assert AVM.url == "https://download.avm.de"
    assert AVM.name == "AVM"
    assert AVM.driver


def test_connection():
    with pytest.raises(WebDriverException):
        AVM = AVMScraper(logger=logger)
        AVM.url = "download"
        AVM.connect_webdriver()


def test_scraping():
    AVM = AVMScraper(logger=logger, max_products=1)
    AVM.scrape_metadata()
    assert len(AVM.catalog) >= 1
