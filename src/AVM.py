'''
Scraper module for AVM vendor
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
        headless: bool,
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

        # Get all links on index page
        elem_list = self.driver.find_elements(By.XPATH, "//pre/a")

        # Depth-first search through list to get to the images
        for index, value in enumerate(elem_list):
            logger.info(f"Searching {value.text}")
            if value.text == "../":
                continue
            elif ".image" in value.text or ".txt" in value.text:
                logger.debug(f"Found file {value.text}")
            else:
                self.driver.get(self.url + value.text)
    
    # Read txt files for metadata
    def read_txt_file(self):
        pass
        
    # Extract Metadata
    def get_metadata(self):
        pass

    # Download firmware
    def download_firmware(self, url: str, file: str):
        self.driver.get(url + file)
