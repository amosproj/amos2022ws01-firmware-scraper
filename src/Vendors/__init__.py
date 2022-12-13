"""
Scraping modules need to be imported in this file to be accessible in core.py
"""

from .AVM.AVM import AVMScraper
from .foscam.foscam import FoscamScraper
from .schneider_electric.schneider_electric import SchneiderElectricScraper
from .scraper import Scraper
from .synology.synology import SynologyScraper
