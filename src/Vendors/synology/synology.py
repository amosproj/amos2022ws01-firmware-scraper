# # Import packages

from datetime import datetime
from typing import Optional, Tuple, Union
from urllib.request import urlopen

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager

from logger import create_logger
from src.Vendors.scraper import Scraper

# # STATICS
VENDOR_URL = 'https://www.synology.com/en-global/support/download/'
PRODUCT_TYPE_SELECTOR = 'div.margin_bottom20 > select:nth-child(1)'
SELECTOR_PRODUCT = '//*[@id="heading_bg"]/div/div/div[2]/select'
SELECTOR_NEWEST_OS = '//*[@id="results"]/div[3]/div[2]/div[1]/div/div[1]/div[1]/div/div/div[1]'
DOWNLOAD_SELECTOR = '//*[@id="results"]/div[3]/div[2]/div[1]/div/div[1]/div[1]/div/div/div[3]/div/div/div/div[1]/a'
SELECTOR_MD5 = '//*[@id="results"]/div[3]/div[2]/div[1]/div/div[1]/div[1]/div/div/div[3]/div/div/div/div[2]/div[2]/div/a'
SELECTOR_DOWNLOAD = '/html/body/div[5]/main/div[1]/div[2]/div[3]/div[2]/div[1]/div/div[1]/div[1]/div/div/div[3]/div/div/div/div[1]/a'
DOWNLOAD_PATH = 'test/'

# Selenium Webdriver Options, Download Path, Headless, Screensize, Webbrowser Version
options = Options()
options.headless = True

options.add_experimental_option("prefs", {
    "download.default_directory": rf"{DOWNLOAD_PATH}"
})

user_agent = 'Synology Download Assistant/1.0'
options.add_argument(f'user-agent={user_agent}')
# # Initialize Chrome and open Vendor Website


class SynologyScraper(Scraper):

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
        self.name = "Synology"
        self.max_products = max_products
        self.driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()), options=options)
        self.driver.implicitly_wait(0.5)  # has to be set only once
        self.logger = logger
        self.current_product_line = ''
        self.current_product = ''
        self.last_checksum = ''
        self.current_release_note_url = ''

    def _create_product_catalog(self) -> dict:
        """clicks once through all product lines and products and saves them in a dict

        Returns:
            dict: product catalog
        """

        sel = Select(self.driver.find_element(
            By.CSS_SELECTOR, value=f"{PRODUCT_TYPE_SELECTOR}"))

        # set keys as product_lines
        product_catalog = dict.fromkeys(
            [elem.text for elem in sel.options[1:]], None)
        # set values from products of product line
        for product in product_catalog.keys():
            sel.select_by_visible_text(product)
            selector_products = Select(self.driver.find_element(
                By.XPATH, value=f"{SELECTOR_PRODUCT}"))
            product_catalog[product] = [
                elem.text for elem in selector_products.options[1:]]
        self.logger.debug('Created product_catalog')
        self.product_catalog = product_catalog
        return product_catalog

    def _choose_product_line(self, product_line: str) -> None:
        """selects product line on vendor website

        Args:
            product_line (str): product line to select
        """
        # select product line
        Select(self.driver.find_element(By.CSS_SELECTOR,
                                        value='div.margin_bottom20 > select:nth-child(1)')).select_by_visible_text(product_line)
        # set current product line
        self.current_product_line = product_line

    def _choose_product(self, product: str) -> None:
        """selects product on vendor website after selecting product line

        Args:
            product (str): product to select
        """
        # select product
        Select(self.driver.find_element(
            By.XPATH, value=f'{SELECTOR_PRODUCT}')).select_by_visible_text(product)
        self.driver.implicitly_wait(1)

    def _has_numbers(self, input_string: str) -> bool:
        # helper function to check if string contains numbers -> then DSM is available
        return any(char.isdigit() for char in input_string)

    def _find_DSM_OS_Version(self) -> Optional[str]:
        """finds newest DSM OS version for selected product

        Returns:
            Optional[str]: newest DSM OS version or None if not found
        """
        try:
            self.driver.implicitly_wait(1)
            # return DSM newest OS Version
            dsm_element = self.driver.find_element(
                By.XPATH, value=f'{SELECTOR_NEWEST_OS}').text
            # if any(char.isdigit() for char in inputString)
            return dsm_element if self._has_numbers(dsm_element) else None
        except Exception as e:
            self.logger.debug(
                f'Could not find DSM OS for {self.current_product}, {self.driver.current_url}')
            self.logger.debug(e)
            return None

    def _get_MD5_checksum(self) -> Optional[str]:
        """gets MD5 checksum for selected product

        Returns:
            str: MD5 checksum
        """
        try:
            el = self.driver.find_element(
                By.XPATH, value=SELECTOR_MD5)
            return el.get_attribute('title').replace('\n(Copy to Clipboard)', '')
        except Exception as e:
            self.logger.debug(
                f'Could not find MD5 checksum in {self.current_product_line}, {self.current_product}, {self.driver.current_url}')
            self.logger.debug(e)
            return None

    def _open_website(self, url: str = '') -> None:
        try:
            if not url:
                url = self.url
            self.driver.get(url)
            self.logger.important(f'Opened Synology website {url}')
        except Exception as e:
            self.logger.error(f"Could not open Synology website {url}!")
            self.logger.error(e)

    def _find_download_link(self) -> Optional[str]:
        """ finds download link for selected product

        Returns:
            str or None: download link
        """
        try:
            download_link = self.driver.find_element(
                By.XPATH, "//*[text()='Download']").get_attribute('href')
            return None if download_link.endswith('.pdf') else download_link
        except Exception as e:
            self.logger.debug(
                f"Download link not found for {self.driver.current_url}")
            self.logger.debug(e)
            return None

    def _download(self, max_no_downloads: int):
        """ downloads all firmwares in firmware_data

        Args:
            firmware_data (list[dict]): list of dicts with firmware data
            max_no_downloads (int): max number of downloads
        """
        for firmware in tqdm(self.product_catalog[:max_no_downloads]):
            for url, filename in zip(firmware["download_links"], firmware["filenames"]):
                save_as = f"out/{filename}"

                with urlopen(url) as file:
                    content = file.read()
                with open(save_as, "wb") as out_file:
                    out_file.write(content)

    def _close_website(self) -> None:
        self.driver.close()
        self.logger.important('Closes Window')

    def _convert_date(self, date_str: str):
        return datetime.strptime(date_str, "%d-%b-%Y").strftime("%Y-%m-%d")

    def _get_release_url(self) -> Optional[str]:
        """gets release url for selected product

        Returns:
            str: release url
        """
        try:
            # TODO have to wait here, as some pages are loaded too slow
            # unfortunately, sometimes it is too slow and the element is not found
            # and
            self.driver.implicitly_wait(2)
            # return URL in Text Release Note
            self.current_release_note_url = self.driver.find_element(
                By.XPATH, "//*[text()='Release Note']").get_attribute('href')
            return self.current_release_note_url
        except Exception as e:
            self.current_release_note_url = ''
            self.logger.debug(
                f'Could not find Release Note on {self.driver.current_url}')
            self.logger.debug(e)
            return None

    def _get_release_date_and_fw_version(self) -> Optional[str]:
        """gets release date for selected product

        Returns:
            str: release date
        """
        original_window = self.driver.current_window_handle
        try:
            #
            if self.current_release_note_url == '':
                self.logger.debug(
                    f'Could not find Release Note on {self.driver.current_url}')
                return None, None
            # Save the current window
            assert len(self.driver.window_handles) == 1
            self.logger.debug('Open new tab')
            self.driver.switch_to.new_window(self.current_release_note_url)
            self.logger.debug('Open Release Page in new tab')
            self._open_website(self.current_release_note_url)
            # send chrome keys to open new tab
            self.logger.debug('Wait until number of windows is 2')
            WebDriverWait(self.driver, 3).until(EC.number_of_windows_to_be(2))
            self.logger.debug('2 windows opened')
            try:
                # find Release Note in new window
                self.logger.debug('Get release date and return')
                html_str = self.driver.find_element(
                    By.CSS_SELECTOR, '#release_notes_content > div.container.margin_bottom80.margin_top80').get_attribute('innerHTML')
                start, end = '<div>', '</div>'
                release_date = html_str[html_str.find(start)+len(start):html_str.rfind(
                    end)].split('\n')[0].replace('</div>', '').replace('(', '').replace(')', '')
                version_str = self.driver.find_element(By.TAG_NAME, 'h3').text
                return release_date, version_str
            except Exception as e:
                self.logger.debug(
                    f'Could not find Release Note on {self.driver.current_url}')
                self.logger.debug(e)
                return None, None
            finally:
                self.logger.debug('Close new tab')
                self.driver.close()
                self.logger.debug('Switch to original tab')
                self.driver.switch_to.window(original_window)
                assert len(self.driver.window_handles) == 1
        except Exception as e:
            self.driver.close()
            self.driver.switch_to.window(original_window)
            self.logger.debug(
                f'Could not find release date in {self.current_product_line}, {self.current_product}, {self.driver.current_url}')
            self.logger.debug(e)
            return None, None

    def scrape_metadata(self) -> list[dict]:
        """function that gets executed from Core.py to scrape metadata
            and search for firmwares

        Returns:
            list[dict]: list of dicts with metadata
        """
        # open website
        self._open_website()
        # create product catalog
        product_catalog = self._create_product_catalog()
        # create list of dicts with metadata
        metadata = []
        for product_line in product_catalog.keys():
            self._choose_product_line(product_line)
            for product in product_catalog[product_line]:
                if len(metadata) > self.max_products:
                    break
                self._choose_product(product)
                tmp_metadata_dict = {'manufacturer': 'Synology',
                                     'product_type': product_line,
                                     'product_name': product,
                                     'url': self.driver.current_url,
                                     'dsm': self._find_DSM_OS_Version(),
                                     'checksum_scraped': self._get_MD5_checksum(),
                                     'download_link': self._find_download_link(),
                                     "additional_data": {}
                                     }
                tmp_metadata_dict['release_url'] = self._get_release_url()
                tmp_metadata_dict['release_date'], tmp_metadata_dict['version'] = self._get_release_date_and_fw_version(
                )
                metadata.append(tmp_metadata_dict)
            self.logger.important(f'Scraped metadata for {product_line}')
        self.logger.important('Scraped metadata for all products')
        self.driver.quit()
        return metadata


if __name__ == '__main__':

    import json

    logger = create_logger()

    logger.important('Start Synology')
    Syn = SynologyScraper(logger)
    metadata = Syn.scrape_metadata()

    # save metadata to json file
    with open("scraped_metadata/firmware_data_Synology.json", "w") as firmware_file:
        json.dump(metadata, firmware_file)

    # download 10 firmwares
    # Syn._download(10)

    logger.important('Finished Synology')
