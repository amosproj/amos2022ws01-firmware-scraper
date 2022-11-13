"""
Main Entrypoint for Firmware Scraper
"""

from AVM import AVMScraper
from utils import setup_logger

url = "ftp.avm.de" 
filename = "fritzbox/fritzbox-5590-fiber/deutschland/fritz.os/FRITZ.Box_5590-07.29.image"

def main():
    AVM = AVMScraper(url=url, headless=True)
    AVM.download_via_ftp()

if __name__ == "__main__":
    import logging

    setup_logger(name="SCRAPER", loglevel="DEBUG")
    logger = logging.getLogger("SCRAPER")
    main()
