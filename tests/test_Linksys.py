import pytest
from src.logger import create_logger
from src.Vendors import LinksysScraper


def test_connection_and_login():
    LS = LinksysScraper(create_logger())
    assert LS.url == "https://www.linksys.com/sitemap"
    assert LS.driver

def test_scrape_product_metadata():
    LS = LinksysScraper(create_logger(), max_products=5)
    scraped_data = LS.scrape_metadata()
    for entry in scraped_data:
        assert entry["manufacturer"] == "Linksys"
        assert entry["product_name"] is not None
        assert entry["product_type"] is not None
        assert entry["version"] is not None
        assert entry["download_link"] is not None
