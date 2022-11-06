'''
Scraper module for AVM vendor
@author: lpagel
'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import logging

logger = logging.getLogger(name="SCRAPER")

class AVM_Scraper:

    def __init__(
        self,
        url: str,
        headless: bool
    ):
        self.url = url
        self.driver = webdriver.Chrome(executable_path="chromedriver_win32")

    def connect_webdriver(self, url: str):
        try:
            self.driver.get(self.url)
            logger.info("Connected Successfully!")
        except Exception as e:
            logger.info(e + ": Could not connect to AVM!")

    # List available downloads
    def get_available_downloads(self):
        self.driver.find_element(By.XPATH, "//pre")
        
    # Extract Metadata
    def get_metadata(self):
        pass

    # Download firmware
    def download_firmware(self):
        pass 
