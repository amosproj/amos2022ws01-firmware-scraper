# # Import packages

import time
from datetime import datetime
from typing import Optional, Tuple, Union

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from src.Vendors.scraper import Scraper

# # STATICS
VENDOR_URL = 'https://www.foscam.com/downloads/index.html'
DOWNLOAD_PATH = 'downloads/'

# Selenium Webdriver Options, Download Path, Headless, Screensize, Webbrowser Version
options = Options()
options.headless = True

options.add_experimental_option("prefs", {
    "download.default_directory": rf"{DOWNLOAD_PATH}"
})

user_agent = 'foscam Download Assistant/1.0'
options.add_argument(f'user-agent={user_agent}')
# # Initialize Chrome and open Vendor Website


class FoscamScraper(Scraper):

    def __init__(
            self,
            logger,
            url: str = VENDOR_URL,
            headless: bool = True,
            options: Options = options,
            max_products: int = float('inf')

    ):
        self.headless = headless
        self.url = url
        self.name = "foscam"
        self.max_products = max_products
        self.driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()), options=options)
        self.driver.implicitly_wait(0.5)  # has to be set only once
        self.logger = logger

    def _open_website(self, url: str = '') -> None:
        try:
            if not url:
                url = self.url
            self.driver.get(url)
            self.logger.debug(f'Opened foscam website {url}')
        except Exception as ex:
            self.logger.error(f"Could not open foscam website {url}!")
            self.logger.error(ex)

    def _close_website(self) -> None:
        self.driver.close()
        self.logger.debug('Closes Window')

    def _get_current_displayed_product_list(self, html) -> list:
        """parses html and returns a list of tuples with product name and product url

        Args:
            html (_type_): html of current product list

        Returns:
            list: list of tuples with product name and product url
        """
        self.driver.implicitly_wait(1)
        product_list = BeautifulSoup(html, 'html.parser').find_all('li')
        products_tuple_list = []
        for product in product_list:
            # append product name and product url
            products_tuple_list.append(
                (product.find_all('a')[1].text, product.find_all('a')[1]['href']))
        return products_tuple_list

    def _next_page(self, counter: int = 0) -> bool:
        """clicks next page button if it exists

        Returns:
            bool: True if next page exists and performs action, False if not
        """
        self.driver.implicitly_wait(1)
        # self.logger.debug(f'{counter = }')
        if counter == 0:
            # do nothing in first run
            return True
        if counter == 1:
            SELECTOR_NEXT_PAGE = '/html/body/div[6]/div[4]/a'
        else:
            SELECTOR_NEXT_PAGE = '/html/body/div[6]/div[4]/a[2]'
        try:
            self.driver.find_element(
                By.XPATH, value=SELECTOR_NEXT_PAGE).click()
            self.driver.implicitly_wait(1)
            return True
        except Exception:
            self.logger.debug('No next page')
            self.logger.debug(f'Found {counter=} pages')
            return False

    def _create_product_catalog(self) -> list:
        """clicks once through all product lines and products and saves them in a dict

        Returns:
            dict: product catalog
        """
        SELECTOR_PRODUCTS = '/html/body/div[6]/div[3]'  # product caroussel
        self.driver.implicitly_wait(1)
        self.logger.debug(f'get html of product caroussel')
        counter = 0
        products_list = []
        self.logger.debug(f'Iterare over pages to create product catalog')
        while self._next_page(counter):
            counter += 1
            time.sleep(2)
            a = self.driver.find_element(
                By.XPATH, value=SELECTOR_PRODUCTS).get_attribute('innerHTML')
            products_list.append(self._get_current_displayed_product_list(a))

        # flat python list
        products_list = [item for sublist in products_list for item in sublist]
        self.products_list = products_list

    def _find_metadata_table(self, product_url: str):
        """scrapes product page and returns a dict with product name, product url, product line, product line url, release note url, release note text, checksum

        Args:
            product_url (str): url of product page
        """

        SELECTOR_METADATA_TABLE = '//*[@id="val"]/div/table'
        self.driver.implicitly_wait(1)
        try:
            product_metadata = self.driver.find_element(
                By.XPATH, value=SELECTOR_METADATA_TABLE).get_attribute('innerHTML')
            self.driver.implicitly_wait(1)
            return product_metadata
        except Exception as ex:
            self.logger.error(ex)
            self.logger.debug('No metadata table, skip product')

    def _convert_date(self, date_str: str):
        try:
            return datetime.strptime(date_str, "%Y/%m/%d").strftime("%Y-%m-%d")
        except Exception as ex:
            self.logger.error(f'Could not convert date {date_str}')
            self.logger.error(ex)
            return None

    def scrape_metadata(self):
        """scrapes metadata from foscam website

        Returns:
            list[dict]: list of dicts with metadata
        """
        self._open_website()
        self._create_product_catalog()

        metadata = []
        self.logger.debug(f'Iterate over product catalog and scrape metadata')
        for product, product_url in self.products_list:
            if len(metadata) > self.max_products:
                break
            try:
                self._open_website(f'https://www.foscam.com{product_url}')
                metadata_html = self._find_metadata_table(product_url)
                fw_releases_list = BeautifulSoup(
                    metadata_html, 'html.parser').find_all('tr')
                for fw_release in fw_releases_list[1:]:
                    metadata_current = fw_release.find_all('td')
                    tmp_metadata_dict = {'manufacturer': 'foscam',
                                         'version': metadata_current[0].text,
                                         'product_type': None,  # not available
                                         'product_name': product,
                                         'url': f'https://www.foscam.com{product_url}',
                                         'checksum_scraped': None,  # not available
                                         'download_link': f"https://www.foscam.com{metadata_current[-1].find_all('a')[0]['href']}",
                                         'release_date': self._convert_date(metadata_current[1].text),
                                         "additional_data": {}  # nothing valuable
                                         }

                    metadata.append(tmp_metadata_dict)
                print(f'Finished scraping {product=}, {product_url=}')
            except Exception as ex:
                self.logger.debug(
                    f'{product=}, {product_url=} is missing crucial data')
                self.logger.debug(ex)
                pass
            time.sleep(1)
        self.driver.quit()
        return metadata


if __name__ == '__main__':
    import json

    from loguru import logger
    logger.debug('Start foscam')
    foscam = FoscamScraper(logger)
    metadata = foscam.scrape_metadata()

    # save metadata to json file
    with open("scraped_metadata/firmware_data_foscam.json", "w") as firmware_file:
        json.dump(metadata, firmware_file)

    logger.debug('Finished foscam')
