"""
Scraper module for AVM vendor
"""

import sys
from datetime import datetime
from os import path

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class AVMScraper:
    def __init__(self, logger, max_products: int = float("inf"), headless: bool = True):
        self.url = "https://download.avm.de"
        self.name = "AVM"
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.fw_types = [".image", ".exe", ".zip", ".dmg"]
        self.catalog = []
        self.headless = headless
        self.logger = logger
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.max_products = max_products

    def connect_webdriver(self):
        try:
            self.driver.get(self.url)
            self.logger.info("Connected Successfully!")
        except Exception as e:
            self.logger.exception("Could not connect to AVM!")
            raise (e)

    # List available firmware downloads
    def scrape_metadata(self) -> list:

        self.connect_webdriver()

        # Get all links on index page
        self.logger.info(f"Scraping all data from {self.url}")

        elem_list = self.driver.find_elements(By.XPATH, "//pre/a")
        elem_list = [
            "/" + elem.text
            for elem in elem_list
            if elem.text not in ["../", "archive/"]
        ]

        # Iterate through index links and append all subdirectories
        for index, value in enumerate(elem_list):
            self.logger.info(f"Searching {value}")
            self.driver.get(self.url + value)
            sub_elems = self.driver.find_elements(By.XPATH, "//pre/a")

            fw_files = [
                (
                    elem.get_property("nextSibling")["data"].split()[0],
                    elem.get_property("pathname"),
                )
                for elem in sub_elems
                if self._get_file_extension(elem.get_property("pathname"))
                in self.fw_types
            ]
            for (date, file) in fw_files:

                firmware_item = {
                    "manufacturer": "AVM",
                    "product_name": None,
                    "product_type": None,
                    "version": None,
                    "release_date": self._convert_date(date),
                    "download_link": None,
                    "checksum_scraped": None,
                    "additional_data": {},
                }

                self.logger.info(f"Found firmware file: {file}")
                text_file = next(
                    (
                        elem.get_property("pathname")
                        for elem in sub_elems
                        if elem.get_property("innerHTML") == "info_en.txt"
                    ),
                    None,
                )
                if text_file:
                    self.logger.info(f"Found info file: {text_file}")
                    product, version = self._parse_txt_file(self.url + text_file)
                    firmware_item["product_name"] = product
                    firmware_item["version"] = version
                    firmware_item["additional_data"] = {
                        "info_url": self.url + text_file
                    }
                firmware_item["download_link"] = self.url + file
                firmware_item["product_type"] = value.strip("/").split("/")[0]
                self.catalog.append(firmware_item)

            if len(self.catalog) >= self.max_products:
                break

            sub_elems = [
                elem.get_property("pathname")
                for elem in sub_elems
                if elem.text != "../"
                and self._get_file_extension(elem.get_property("pathname"))
                not in [".txt", ".image", ".exe", ".zip", ".dmg"]
            ]
            elem_list.extend(sub_elems)
        return self.catalog

    def _get_file_extension(self, filename):
        return path.splitext(filename)[-1]

    # TODO: Parse text files other than info_txt.en
    def _parse_txt_file(self, file_url: str):

        product, version = None, None
        try:
            txt = requests.get(file_url).text.splitlines()
            product = self._get_partial_str(txt, "Product").split(":")[-1].strip()
            version = self._get_partial_str(txt, "Version").split(":")[-1].strip()
            self.logger.info(f"Found {product, version} in txt file!")
        except Exception as e:
            self.logger.info(f"Could not parse text file: {e}")

        return product, version

    def _get_partial_str(self, txt: list, query: str):
        return [s for s in txt if query in s][0]

    def _convert_date(self, date_str: str):
        return datetime.strptime(date_str, "%d-%b-%Y").strftime("%Y-%m-%d")


if __name__ == "__main__":

    import json

    from src.logger_old import create_logger_old

    logger = create_logger_old()
    AVM = AVMScraper(logger=logger)
    firmware_data = AVM.scrape_metadata()

    with open("scraped_metadata/firmware_data_AVM.json", "w") as firmware_file:
        json.dump(firmware_data, firmware_file)
