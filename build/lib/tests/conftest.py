import pytest

from src.logger import create_logger
from src.Vendors.synology.synology import Synology_scraper

logger = create_logger()


@pytest.fixture(scope="session")
def Synology():
    """Create Synology_scraper class object"""
    return Synology_scraper(logger=logger)
