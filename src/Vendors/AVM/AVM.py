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
import pandas as pd


class AVMScraper:

    def __init__(
        self
    ):
        self.url = "https://download.avm.de/"
        self.name = "AVM"
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.catalog = []

    def connect_webdriver(self):
        try:
            self.driver.get(self.url)
            logging.info("Connected Successfully!")
        except Exception as e:
            logging.info(e + ": Could not connect to AVM!")

    # List available firmware downloads
    def get_all_files(self):
        
        # Get all links on index page
    
        text_files = []
        fw_files = []

        elem_list = self.driver.find_elements(By.XPATH, "//pre/a")
        elem_list = [elem.text for elem in elem_list if elem.text not in ["../", "archive/"]]
        
        # Iterate through index links and append all subdirectories
        # TODO: Build tuple like (txt_file, fw_file)
        for index, value in enumerate(elem_list):
            print(f"Searching {value}")
            self.driver.get(self.url + value)
            sub_elems = self.driver.find_elements(By.XPATH, "//pre/a")

            text_files.extend([elem.get_property("pathname") for elem in sub_elems if self.get_file_extension(elem.get_property("pathname")) == ".txt"])
            fw_files.extend([elem.get_property("pathname") for elem in sub_elems if self.get_file_extension(elem.get_property("pathname")) in [".image", ".exe"]])
            sub_elems = [elem.get_property("pathname") for elem in sub_elems if elem.text != "../" and self.get_file_extension(elem.get_property("pathname")) not in [".txt", ".image", ".exe", ".zip"]]
            elem_list.extend(sub_elems)
        return text_files, fw_files
 
    def scrape_metadata_via_ftp(self) -> list:

        dict_ = {}

        with ftputil.FTPHost("ftp.avm.de", "anonymous", "") as ftp_host:

            products = ftp_host.listdir(ftp_host.curdir)
            products.remove("archive")
            for product in products:
                for root, dirs, files in ftp_host.walk(product):
                    if not any(_ for _ in files if self.get_file_extension(_)=='.image'):
                        continue
                    else:
                        if not any(_ for _ in files if self.get_file_extension(_)=='.txt'):
                            print("No info.txt available.")
                            dict_["manufacturer"].append("AVM")
                            dict_["product_name"].append(root.split("/")[1])
                            dict_["product_type"].append("NA")
                            dict_["version"].append("NA")
                            dict_["release_date"].append("NA")
                            dict_["checksum_scraped"].append("NA")
                            dict_["download_link"].append("NA")
                            dict_["additional_data"] = {}
                        else:
                            for f in files:
                                if f == "info_en.txt":
                                    txt = self.read_txt_file(f)
               
    def get_file_extension(self, filename):
        return path.splitext(filename)[-1]

    # TODO: Parse txt files for metadata
    def read_txt_file(self, filename) -> dict:
        pass

    # Download firmware
    def download_firmware(self, filename, target_dir):
        pass
        
if __name__ == '__main__':

    AVM = AVMScraper()
    AVM.connect_webdriver()
    txt, img = AVM.get_all_files()