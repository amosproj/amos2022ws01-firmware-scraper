"""
Scraper module for AVM vendor
"""

from os import path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import logging
import ftputil


class AVMScraper:

    def __init__(
        self
    ):
        self.url = "https://download.avm.de/"
        self.name = "AVM"
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def connect_webdriver(self):
        try:
            self.driver.get(self.url)
            logging.info("Connected Successfully!")
        except Exception as e:
            logging.info(e + ": Could not connect to AVM!")

    # List available firmware downloads
    def get_products(self):

        self.connect_webdriver()

        # Get all links on index page
        elem_list = self.driver.find_elements(By.XPATH, "//pre/a")

        for index, value in enumerate(elem_list):
            logging.info(f"Searching {value.text}")
            if value.text == "../":
                continue
            elif ".image" in value.text or ".txt" in value.text:
                logging.debug(f"Found file {value.text}")
            else:
                self.driver.get(self.url + value.text)

    def download_via_ftp(self):
        with ftputil.FTPHost(self.url, "anonymous", "") as ftp_host:

            products = ftp_host.listdir(ftp_host.curdir)
            products.remove("archive")
            #import pdb;pdb.set_trace()
            for product in products:
                for root, dirs, files in ftp_host.walk(product):
                    # import pdb;pdb.set_trace()
                    if not any(_ for _ in files if self.get_file_extension(_)=='.image'):
                        continue
                    else:
                        for f in files:
                            if self.get_file_extension(f) == ".image":
                                logger.info(f"Downloading {f}")
                                import pdb;pdb.set_trace()
                                ftp_host.download(root+"/"+f, "firmware/"+f)

                        
    def get_file_extension(self, filename):
        return path.splitext(filename)[-1]

    # Read txt files for metadata
    def read_txt_file(self):
        pass

    # Download firmware
    def download_firmware(self, url: str, file: str):
        self.driver.get(url + file)
