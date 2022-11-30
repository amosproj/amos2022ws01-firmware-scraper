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
from urllib.request import urlopen

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from src.Vendors.scraper import Scraper
from src.logger import create_logger

DOWNLOAD_URL_GLOBAL = (
    "https://www.se.com/ww/en/download/doc-group-type/3541958-Software%20&%20Firmware/?docType=1555893-Firmware"
)
DOWNLOAD_URL_GERMANY = (
    "https://www.se.com/de/de/download/doc-group-type/7090926-Software%20und%20Firmware/?docType=1555893-Firmware"
)
DOWNLOAD_URL_USA = (
    "https://www.se.com/us/en/download/doc-group-type/3587139-Software%20&%20Firmware/?docType=1555893-Firmware"
)


class SchneiderElectricScraper(Scraper):
    def __init__(
        self,
        logger,
        scrape_entry_url: str = DOWNLOAD_URL_GLOBAL,
        max_products: int = float("inf"),
    ):
        self.scrape_entry_url = scrape_entry_url
        self.max_products = max_products

        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        self.driver.implicitly_wait(0.5)  # has to be set only once

        self.logger = logger

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
        CSS_SELECTOR_DOWNLOAD_URL = ".file-download"
        PATTERN = r"&p_File_Name=([\w\-\.\+\ ]+\.[\w]+)"

        # here, we accept multiple found elements
        urls = [
            el.get_attribute("href")
            for el in product_page.find_elements(by=By.CSS_SELECTOR, value=CSS_SELECTOR_DOWNLOAD_URL)
        ]

        non_pdf_urls = []
        non_pdf_filenames = []
        for url in urls:
            match = re.search(PATTERN, url)
            if match and not match.group().endswith("pdf"):
                non_pdf_urls.append(url)
                non_pdf_filenames.append(match.group(1))
        return non_pdf_urls, non_pdf_filenames

    def _extract_info(self, product_url: str) -> list[dict]:
        CSS_SELECTOR_TITLE = ".doc-title"
        CSS_SELECTOR_RELEASE_DATE = ".doc-details-desktop > div:nth-child(1) > span:nth-child(1)"
        CSS_SELECTOR_LANGUAGES = ".doc-details-desktop > div:nth-child(2) > span:nth-child(1)"
        CSS_SELECTOR_VERSION = ".doc-details-desktop > div:nth-child(2) > span:nth-child(2)"
        CSS_SELECTOR_REFERENCE = "div.col-md-12:nth-child(3) > span:nth-child(1)"
        CSS_SELECTOR_PRODUCT_RANGES = ".range-block > .inner-1"

        title = release_date = languages = version = reference = product_ranges = None

        self.driver.get(product_url)
        product_page = self.driver.find_element(by=By.TAG_NAME, value="html")

        if el := self._find_element_and_check(product_page, By.CSS_SELECTOR, CSS_SELECTOR_TITLE):
            # Some product titles are accompanied by an information stroke element. If it exists, it corrupts the
            # extracted title. Therefore, it is removed (if existent).
            title = " ".join(el.text.split()).removesuffix("information_stroke").rstrip()
        if el := self._find_element_and_check(product_page, By.CSS_SELECTOR, CSS_SELECTOR_RELEASE_DATE):
            release_date_raw = el.text.removeprefix("Date : ").split("/")
            release_date = f"{release_date_raw[2]}-{release_date_raw[1]}-{release_date_raw[0]}"
        if el := self._find_element_and_check(product_page, By.CSS_SELECTOR, CSS_SELECTOR_LANGUAGES):
            languages = el.text.removeprefix("Languages : ")
        if el := self._find_element_and_check(product_page, By.CSS_SELECTOR, CSS_SELECTOR_VERSION):
            version = el.text.removeprefix("Latest Version : ")
        if el := self._find_element_and_check(product_page, By.CSS_SELECTOR, CSS_SELECTOR_REFERENCE):
            reference = el.text.removeprefix("Reference : ")
        if el := self._find_element_and_check(product_page, By.CSS_SELECTOR, CSS_SELECTOR_PRODUCT_RANGES):
            product_ranges = el.text.removeprefix("Product Ranges: ")

        firmware_item = {
            "manufacturer": "SchneiderElectric",
            "product_name": title,
            "product_type": product_ranges,
            "version": version,
            "release_date": release_date,
            "checksum_scraped": None,
            "additional_data": {"product_reference": reference, "languages": languages},
        }

        download_links, filenames = self._identify_downloads(product_page)

        if len(download_links) == 0:
            self.logger.debug(
                f"Could not find a download link for product '{title}' with URL '{product_url}'."
                f" This could mean that only PDFs where associated with the product or that the URL is broken."
            )
            return []
        elif len(download_links) == 1:
            firmware_item["download_link"] = download_links[0]
            self.logger.info(f"Scraped product '{title}'.")
            return [firmware_item]
        elif len(download_links) > 1:
            self.logger.debug(f"Found multiple download links for product '{title}' with URL '{product_url}'.")
            # When multiple (non-PDF) download links for a single product are found, a separate metadata dict for every
            # link is returned
            firmware_item_list = []
            for link in download_links:
                firmware_item_copy = firmware_item.copy()
                firmware_item_copy["download_link"] = link
                firmware_item_copy["additional_data"]["other_download_links"] = download_links
                firmware_item_list.append(firmware_item_copy)
            self.logger.info(f"Scraped product '{title}'.")
            return firmware_item_list

    def scrape_metadata(self) -> list[dict]:
        self.driver.get(self.scrape_entry_url)
        self.logger.info(f"Successfully accessed entry point URL {self.scrape_entry_url}.")

        # on a single page, only a certain number (e.g. 10) of firmware products is displayed
        # pages must be iterated to retrieve all elements
        no_pages = int(
            self.driver.find_element(by=By.CLASS_NAME, value="pager").find_element(by=By.CLASS_NAME, value="last").text
        )

        # iterate over result pages
        firmware_product_urls = []
        for page in range(1, no_pages + 1):
            self.driver.get(f"{self.scrape_entry_url}&pageNumber={page}")

            firmware_products = self.driver.find_element(by=By.CLASS_NAME, value="result-list").find_elements(
                by=By.CLASS_NAME, value="result-list-item"
            )
            firmware_product_urls += [
                item.find_element(by=By.CLASS_NAME, value="title").get_attribute("href") for item in firmware_products
            ]
            if len(firmware_product_urls) > self.max_products:
                break

        self.logger.info(
            f"Identified {self.max_products} firmware products."
            f" (If a maximum number of products to scrape was given, there could be more.)"
        )
        self.logger.info(f"Start scraping metadata of firmware products.")

        # iterate over found products
        extracted_data = []
        for product_url in firmware_product_urls[: self.max_products]:
            if firmware_items := self._extract_info(product_url):
                extracted_data += firmware_items

        self.logger.info(f"Finished scraping metadata of firmware products. Return metadata to core.")
        return extracted_data


def _download(firmware_data: list[dict], max_no_downloads: int):
    for firmware in tqdm(firmware_data[:max_no_downloads]):
        for url, filename in zip(firmware["download_links"], firmware["filenames"]):
            save_as = f"out/{filename}"

            with urlopen(url) as file:
                content = file.read()
            with open(save_as, "wb") as out_file:
                out_file.write(content)


if __name__ == "__main__":
    logger = create_logger()
    scraper = SchneiderElectricScraper(logger, DOWNLOAD_URL_GLOBAL, max_products=20)
    firmware_data = scraper.scrape_metadata()
    with open("../../../test/files/firmware_data_schneider.json", "w") as firmware_file:
        json.dump(firmware_data, firmware_file)

    print("Start downloading:")
    _download(firmware_data, 0)
    print("Finished download.")
