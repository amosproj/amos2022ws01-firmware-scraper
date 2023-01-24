"""
Scraping modules need to be imported in this file to be accessible in core.py
"""

from .AVM.AVM import AVMScraper
from .foscam.foscam import FoscamScraper
from .schneider_electric.schneider_electric import SchneiderElectricScraper
from .tp_link.tp_link import TPLinkScraper
from .scraper import Scraper
from .synology.synology import SynologyScraper
from .Rockwell.Rockwell_scraper import RockwellScraper
from .swisscom.swisscom import SwisscomScraper
from .Zyxel.Zyxel import ZyxelScraper
from .dd_wrt.dd_wrt import DDWRTScraper
from .Engenius.Engenius import EngeniusScraper
from .DLink.DLink import DLinkScraper
from .Qnap.Qnap import QnapScraper
from .Netgear.Netgear import NetgearScraper
from .ABB.ABB import ABBScraper
from .Trendnet.Trendnet import TrendnetScraper
from .Linksys.Linksys_scraper import LinksysScraper
