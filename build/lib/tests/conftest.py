import pytest

from logger import create_logger
from Vendors.synology.synology import Synology_scraper

logger = create_logger()


@pytest.fixture(scope="session")
def Synology():
    """Create Synology_scraper class object"""
    return Synology_scraper(logger=logger)
