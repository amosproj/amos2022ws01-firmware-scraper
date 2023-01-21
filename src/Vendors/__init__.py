"""
Scraping modules need to be imported in this file to be accessible in core.py
"""


from .ABB.ABB import ABBScraper
from .AVM.AVM import AVMScraper
from .Belkin.Belkin import BelkinScraper
from .dd_wrt.dd_wrt import DDWRTScraper
from .Engenius.Engenius import EngeniusScraper
from .foscam.foscam import FoscamScraper
from .Gigaset.Gigaset import GigasetScraper
from .Rockwell.Rockwell_scraper import RockwellScraper
from .schneider_electric.schneider_electric import SchneiderElectricScraper
from .scraper import Scraper
from .swisscom.swisscom import SwisscomScraper
from .synology.synology import SynologyScraper
from .tp_link.tp_link import TPLinkScraper
from .Trendnet.Trendnet import TrendnetScraper
from .Zyxel.Zyxel import ZyxelScraper
