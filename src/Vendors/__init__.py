"""
Scraping modules need to be imported in this file to be accessible in core.py
"""

from synology.synology import Synology_scraper

from .AVM.AVM import AVMScraper
from .schneider_electric.schneider_electric import SchneiderElectricScraper
from .synology.synology import Synology_scraper
