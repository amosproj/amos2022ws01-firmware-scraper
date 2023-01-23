import pytest

from src.logger import create_logger
from src.Vendors.synology.synology import SynologyScraper

logger = create_logger()


@pytest.fixture(scope="session")
def Synology():
    """Create Synology_scraper class object"""
    return SynologyScraper(logger=logger)


@pytest.fixture(scope="session")
def product_catalog(Synology: SynologyScraper.__init__) -> dict:
    """Create Synology_scraper class object"""
    return Synology._create_product_catalog()
