import pytest
from src.logger_old import create_logger_old
from src.Vendors import LinksysScraper


def test_connection_and_login():
    LS = LinksysScraper(create_logger_old())
    assert LS.url == "https://www.linksys.com/sitemap"
    assert LS.driver


def test_scrape_product_metadata():
    LS = LinksysScraper(create_logger_old(), max_products=5)
    scraped_data = LS.scrape_metadata()
    for entry in scraped_data:
        assert entry["manufacturer"] == "Linksys"
        assert entry["product_name"] is not None
        assert entry["product_type"] is not None
        assert entry["version"] is not None
        assert entry["download_link"] is not None
