import pytest

from src.logger_old import create_logger_old
from src.Vendors.synology.synology import SynologyScraper

logger = create_logger_old()


@pytest.fixture(scope="session")
def Synology():
    """Create Synology_scraper class object"""
    return SynologyScraper(logger=logger)


@pytest.fixture(scope="session")
def product_catalog(Synology: SynologyScraper.__init__) -> dict:
    """Create Synology_scraper class object"""
    return Synology._create_product_catalog()
