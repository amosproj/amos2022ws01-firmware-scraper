"""
Scraping modules need to be imported in this file to be accessible in core.py
"""

from .AVM.AVM import AVMScraper
from .foscam.foscam import FoscamScraper
from .schneider_electric.schneider_electric import SchneiderElectricScraper
from .tp_link.tp_link import TPLinkScraper
from .scraper import Scraper
from .synology.synology import SynologyScraper
from .swisscom.swisscom import SwisscomScraper
