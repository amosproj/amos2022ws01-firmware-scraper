'''
Main Entrypoint for Firmware Scraper
'''

from AVM import AVM_Scraper
from utils import setup_logger

url = "https://download.avm.de/" 
filename = "fritzbox/fritzbox-5590-fiber/deutschland/fritz.os/FRITZ.Box_5590-07.29.image"

def main():
    AVM = AVM_Scraper(url=url, headless=True)
    AVM.connect_webdriver(url)
    AVM.download_firmware(url, filename)

if __name__ == "__main__":
    import logging

    setup_logger(name="SCRAPER", loglevel="DEBUG")
    logger = logging.getLogger("SCRAPER")
    main()
