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

from src.logger import *


class AVMScraper:
    def __init__(self, max_products: int = float("inf")):
        self.url = "https://download.avm.de"
        self.name = "AVM"
        self.fw_types = [".image", ".exe", ".zip", ".dmg"]
        self.catalog = []
        self.logger = get_logger()
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=self.options
        )
        self.max_products = max_products

    def connect_webdriver(self):
        try:
            self.driver.get(self.url)
            self.logger.info(entry_point_url_success(self.url))
        except Exception as e:
            self.logger.error(entry_point_url_failure(self.url))
            raise (e)

    # TODO: Scrape product name
    def scrape_metadata(self) -> list:

        self.connect_webdriver()

        # Get all links on index page
        self.logger.important(start_scraping())

        elem_list = self.driver.find_elements(By.XPATH, "//pre/a")
        elem_list = [
            "/" + elem.text
            for elem in elem_list
            if elem.text not in ["../", "archive/"]
        ]

        # Iterate through index links and append all subdirectories
        for index, value in enumerate(elem_list):

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

                text_file = next(
                    (
                        elem.get_property("pathname")
                        for elem in sub_elems
                        if elem.get_property("innerHTML") == "info_en.txt"
                    ),
                    None,
                )
                if text_file:

                    product, version = self._parse_txt_file(self.url + text_file)
                    firmware_item["product_name"] = product
                    firmware_item["version"] = version
                    firmware_item["additional_data"] = {
                        "info_url": self.url + text_file
                    }
                firmware_item["download_link"] = self.url + file
                firmware_item["product_type"] = value.strip("/").split("/")[0]
                self.catalog.append(firmware_item)
                self.logger.info(
                    firmware_scraping_success(firmware_item["product_type"])
                )

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

        self.logger.important(finish_scraping())
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
        except Exception as e:
            pass

        return product, version

    def _get_partial_str(self, txt: list, query: str):
        return [s for s in txt if query in s][0]

    def _convert_date(self, date_str: str):
        return datetime.strptime(date_str, "%d-%b-%Y").strftime("%Y-%m-%d")


if __name__ == "__main__":

    import json

    AVM = AVMScraper()
    firmware_data = AVM.scrape_metadata()

    with open("scraped_metadata/firmware_data_AVM.json", "w") as firmware_file:
        json.dump(firmware_data, firmware_file)
