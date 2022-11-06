'''
Main Entrypoint for Firmware Scraper
'''

from AVM import AVM_Scraper
from utils import setup_logger

url = "https://download.avm.de/" 

def main():
    AVM = AVM_Scraper(url=url, headless=True)
    AVM.connect_webdriver(url)
    #AVM.get_available_downloads()


if __name__ == "__main__":
    import logging

    setup_logger(name="SCRAPER", loglevel="DEBUG")
    logger = logging.getLogger("SCRAPER")
    main()
