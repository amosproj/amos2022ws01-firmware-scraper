"""
Schneider Electric (SE) has a unified interface for accessing software downloads: DOWNLOAD_URL_*.
One of the categories is 'firmware'.
Depending on the selected website region, the number of available downloads varies.
As of 22-11-06, region 'Global' (DOWNLOAD_URL_GLOBAL) provides the highest number of downloads, which is therefore
selected as default.

Even when category 'firmware' is selected, some displayed products are just release notes with no associated binary.
These products are therefore filtered out.
"""
import json
import re
from tqdm import tqdm
from typing import Optional

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.firefox import GeckoDriverManager
from urllib.request import urlopen


DOWNLOAD_URL_GLOBAL = 'https://www.se.com/ww/en/download/doc-group-type/3541958-Software%20&%20Firmware/?docType=1555893-Firmware'
DOWNLOAD_URL_GERMANY = 'https://www.se.com/de/de/download/doc-group-type/7090926-Software%20und%20Firmware/?docType=1555893-Firmware'
DOWNLOAD_URL_USA = 'https://www.se.com/us/en/download/doc-group-type/3587139-Software%20&%20Firmware/?docType=1555893-Firmware'


class SchneiderElectricScraper:

    def __init__(self, scrape_entry_url: str):
        self.scrape_entry_url = scrape_entry_url

    def _find_element_and_check(self, product_page: WebElement, by: By, value: str) -> Optional[WebElement]:
        # we use find_elements instead of find_element to be aware if the CSS selector is able to locate a unique element
        elements = product_page.find_elements(by=by, value=value)

        # if multiple elements are found using one selector, we return None, as we don't know if we found the right one
        if len(elements) > 1:
            return None
        elif len(elements) == 1:
            return elements[0]
        else:
            return None

    def _identify_downloads(self, product_page: WebElement) -> (list, list):
        CSS_SELECTOR_DOWNLOAD_URL = '.file-download'
        PATTERN = r'&p_File_Name=([\w\-\.\+\ ]+\.[\w]+)'

        # here, we accept multiple found elements
        urls = [el.get_attribute('href') for el in product_page.find_elements(by=By.CSS_SELECTOR, value=CSS_SELECTOR_DOWNLOAD_URL)]

        non_pdf_urls = []
        non_pdf_filenames = []
        for url in urls:
            match = re.search(PATTERN, url)
            if match and not match.group().endswith('pdf'):
                non_pdf_urls.append(url)
                non_pdf_filenames.append(match.group(1))
        return non_pdf_urls, non_pdf_filenames

    def _extract_info(self, product_page: WebElement) -> dict:
        CSS_SELECTOR_TITLE = '.doc-title'
        CSS_SELECTOR_RELEASE_DATE = '.doc-details-desktop > div:nth-child(1) > span:nth-child(1)'
        CSS_SELECTOR_LANGUAGES = '.doc-details-desktop > div:nth-child(2) > span:nth-child(1)'
        CSS_SELECTOR_VERSION = '.doc-details-desktop > div:nth-child(2) > span:nth-child(2)'
        CSS_SELECTOR_REFERENCE = 'div.col-md-12:nth-child(3) > span:nth-child(1)'
        CSS_SELECTOR_PRODUCT_RANGES = '.range-block > .inner-1'

        title = release_date = languages = version = reference = product_ranges = None

        if el := self._find_element_and_check(product_page, By.CSS_SELECTOR, CSS_SELECTOR_TITLE):
            title = el.text
        if el := self._find_element_and_check(product_page, By.CSS_SELECTOR, CSS_SELECTOR_RELEASE_DATE):
            release_date = el.text.removeprefix("Date : ")
        if el := self._find_element_and_check(product_page, By.CSS_SELECTOR, CSS_SELECTOR_LANGUAGES):
            languages = el.text.removeprefix("Languages : ")
        if el := self._find_element_and_check(product_page, By.CSS_SELECTOR, CSS_SELECTOR_VERSION):
            version = el.text.removeprefix("Latest Version : ")
        if el := self._find_element_and_check(product_page, By.CSS_SELECTOR, CSS_SELECTOR_REFERENCE):
            reference = el.text.removeprefix("Reference : ")
        if el := self._find_element_and_check(product_page, By.CSS_SELECTOR, CSS_SELECTOR_PRODUCT_RANGES):
            product_ranges = el.text.removeprefix("Product Ranges: ")

        firmware_item = {"manufacturer": "Schneider Electric",
                         "product_name": title,
                         "product_type": product_ranges,
                         "version": version,
                         "release_date": release_date,
                         "checksum_scraped": None,
                         "additional_data": {
                             "product_reference": reference,
                             "languages": languages
                         }
                        }

        download_links, filenames = self._identify_downloads(product_page)

        if len(download_links) == 0:
            return {}
        elif len(download_links) >= 1:
            firmware_item["download_link"] = download_links[0]
            firmware_item["additional_data"]["all_download_links"] = download_links
            firmware_item["additional_data"]["all_filenames"] = filenames

        return firmware_item


    def scrape_metadata(self, max_no_products: int = None) -> list[dict]:
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        driver.implicitly_wait(0.5)  # has to be set only once

        driver.get(self.scrape_entry_url)

        # on a single page, only a certain number (e.g. 10) of firmware products is displayed
        # pages must be iterated to retrieve all elements
        no_pages = int(driver.find_element(by=By.CLASS_NAME, value="pager").find_element(by=By.CLASS_NAME, value="last").text)

        # iterate over result pages
        firmware_product_urls = []
        for page in range(1, no_pages+1):
            driver.get(f"{self.scrape_entry_url}&pageNumber={page}")

            firmware_products = driver.find_element(by=By.CLASS_NAME, value='result-list').find_elements(by=By.CLASS_NAME, value='result-list-item')
            firmware_product_urls += [item.find_element(by=By.CLASS_NAME, value='title').get_attribute('href') for item in firmware_products]
            if len(firmware_product_urls) >= max_no_products: break

        # iterate over found products
        extracted_data = []
        for product in tqdm(firmware_product_urls[:max_no_products]):
            driver.get(product)
            product_page = driver.find_element(by=By.TAG_NAME, value='html')
            if firmware_item := self._extract_info(product_page):
                extracted_data.append(firmware_item)

        driver.quit()
        return extracted_data


def download(firmware_data: list[dict], max_no_downloads: int):
    for firmware in tqdm(firmware_data[:max_no_downloads]):
        for url, filename in zip(firmware['download_links'], firmware['filenames']):
            save_as = f'out/{filename}'

            with urlopen(url) as file:
                content = file.read()
            with open(save_as, 'wb') as out_file:
                out_file.write(content)


if __name__ == '__main__':
    scraper = SchneiderElectricScraper(DOWNLOAD_URL_GLOBAL)
    print('Start scraping:')
    firmware_data = scraper.scrape_metadata(50)
    print('Finished scraping.')
    with open('../../../test/files/firmware_data_schneider.json', 'w') as firmware_file:
        json.dump(firmware_data, firmware_file)

    print('Start downloading:')
    download(firmware_data, 0)
    print('Finished download.')

