"""
Scraper module for Cisco vendor
"""

import time
from datetime import datetime
from os import path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class CiscoScraper:
    def __init__(self, logger, max_products: int = float("inf"), headless: bool = True):
        self.url = "https://software.cisco.com/download/home/286304649"
        self.name = "Cisco"
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
            self.logger.exception("Could not connect to Cisco!")
            raise (e)

    # TODO: Either change scraping method to use product list OR try to catch other formats
    def scrape_metadata(self) -> list:

        self.connect_webdriver()
        time.sleep(5)

        prod_ctr, main_ctr, sub_ctr = 1, 1, 1

        prod_list = self.driver.find_elements(
            By.CSS_SELECTOR, "#product-category-list > li"
        )
        self.logger.info(f"Found {len(prod_list)} product categories.")

        while prod_ctr <= len(prod_list):

            prod_elem = self.driver.find_element(
                By.CSS_SELECTOR, f"#product-category-list > li:nth-child({prod_ctr})"
            )
            self.logger.info(
                f"Scraping prod category: {prod_elem.get_attribute('innerText')}."
            )
            prod_elem.click()
            time.sleep(5)
            main_list = self.driver.find_elements(
                By.CSS_SELECTOR, "#main-category-list > li"
            )
            while main_ctr <= len(main_list):
                main_elem = self.driver.find_element(
                    By.CSS_SELECTOR, f"#main-category-list > li:nth-child({main_ctr})"
                )
                self.logger.info(
                    f"Scraping main category: {main_elem.get_attribute('innerText')}."
                )
                main_elem.click()
                time.sleep(5)
                sub_list = self.driver.find_elements(
                    By.CSS_SELECTOR, "#sub-category-list > li"
                )
                while sub_ctr <= len(sub_list):
                    sub_elem = self.driver.find_element(
                        By.CSS_SELECTOR, f"#sub-category-list > li:nth-child({sub_ctr})"
                    )
                    self.logger.info(
                        f"Scraping sub category: {sub_elem.get_attribute('innerText')}."
                    )

                    sub_elem.click()
                    time.sleep(5)
                    self.catalog.append(self._handle_firmware_page())
                    sub_ctr += 1
                    self.driver.back()
                    time.sleep(5)
                    self._refresh_elems(prod_ctr, main_ctr)
                main_ctr += 1
            prod_ctr += 1

        return self.catalog

    def _refresh_elems(self, prod_ctr, main_ctr):
        self.driver.find_element(
            By.CSS_SELECTOR, f"#product-category-list > li:nth-child({prod_ctr})"
        ).click()
        time.sleep(5)
        self.driver.find_element(
            By.CSS_SELECTOR, f"#main-category-list > li:nth-child({main_ctr})"
        ).click()

    def _handle_firmware_page(self) -> dict:
        firmware_item = {
            "manufacturer": "Cisco",
            "product_name": None,
            "product_type": None,
            "version": None,
            "release_date": None,
            "download_link": None,
            "checksum_scraped": None,
            "additional_data": {},
        }
        return firmware_item


if __name__ == "__main__":

    import json

    from src.logger import create_logger

    logger = create_logger(level="INFO")
    Cisco = CiscoScraper(logger=logger)
    firmware_data = Cisco.scrape_metadata()

    with open("scraped_metadata/firmware_data_Cisco.json", "w") as fw_file:
        json.dump(firmware_data, fw_file)
