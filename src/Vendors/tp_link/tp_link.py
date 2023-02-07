import json

from selenium.common import WebDriverException
from selenium.webdriver.common.by import By


from src.logger import *
from src.Vendors.scraper import Scraper

DOWNLOAD_URL_GLOBAL = "https://www.tp-link.com/en/support/download/"


class TPLinkScraper(Scraper):
    def __init__(
        self,
        driver,
        scrape_entry_url: str = DOWNLOAD_URL_GLOBAL,
        headless: bool = True,
        max_products: int = float("inf"),
    ):
        self.logger = get_logger()
        self.scrape_entry_url = scrape_entry_url
        self.headless = headless
        self.max_products = max_products
        self.name = "TP-Link"
        self.driver = driver
        # self.driver.implicitly_wait(0.5)  # has to be set only once

    def _clean_up_product_category(self, product_category: str) -> str:
        if ">" in product_category:
            product_category_substrings = [substring.strip() for substring in product_category.split(">")]
            product_category = product_category_substrings[-1]

            # deal with special cases, where multiple substrings are necessary to describe the product category
            for s in ["Mesh Wi-Fi", "Omada Cloud SDN", "Omada Access Points"]:
                if s in product_category_substrings:
                    product_category = ", ".join(product_category_substrings[1:])
                    break

        return product_category

    def _scrape_product_metadata(self, product_url: str, product_category: str) -> dict:
        CSS_SELECTOR_FIRMWARE = "a[href='#Firmware']"
        CSS_SELECTOR_PRODUCT_NAME = "#model-version-name"
        CSS_SELECTOR_HARDWARE_VERSION = "#verison-hidden"
        CSS_SELECTOR_SOFTWARE_VERSION = "#content_Firmware > table > tbody > tr.basic-info > th.download-resource-name"
        CSS_SELECTOR_RELEASE_DATE = (
            "#content_Firmware > table > tbody > tr.detail-info > td:nth-child(1) > span:nth-child(2)"
        )
        CSS_SELECTOR_DOWNLOAD_LINK_SIMPLE = (
            "#content_Firmware > table > tbody > tr.basic-info > th.download-resource-btnbox > a"
        )
        CSS_SELECTOR_DOWNLOAD_LINK_GLOBAL = "#content_Firmware > table > tbody > tr.basic-info > th.download-resource-btnbox > div > div > div > a.tp-dialog-btn.tp-dialog-btn-white.ga-click"

        # access product page
        try:
            self.driver.get(product_url)
        except WebDriverException as e:
            self.logger.warning(firmware_url_failure(product_url))
            return {}

        # check if firmware download is offered
        try:
            self.driver.find_element(by=By.CSS_SELECTOR, value=CSS_SELECTOR_FIRMWARE).click()
        except WebDriverException as e:
            self.logger.info(f"No firmware found for URL {product_url}.")
            return {}

        product_name = version = release_date = download_link = None

        # scrape product name
        try:
            product_name = self.driver.find_element(by=By.CSS_SELECTOR, value=CSS_SELECTOR_PRODUCT_NAME).text
            hardware_version = self.driver.find_element(by=By.CSS_SELECTOR, value=CSS_SELECTOR_HARDWARE_VERSION).text
            product_name = product_name + hardware_version
        except WebDriverException as e:
            self.logger.debug(attribute_scraping_failure(f"product name for '{product_url}'"))

        # scrape version
        try:
            resource_name = self.driver.find_element(by=By.CSS_SELECTOR, value=CSS_SELECTOR_SOFTWARE_VERSION).text
            version = "_".join(resource_name.split("_")[1:])  # remove product name from version
        except Exception as e:
            self.logger.debug(attribute_scraping_failure(f"version for '{product_url}'"))

        # scrape release date
        try:
            release_date = self.driver.find_element(by=By.CSS_SELECTOR, value=CSS_SELECTOR_RELEASE_DATE).text.rstrip()
        except Exception as e:
            self.logger.debug(attribute_scraping_failure(f"release date for '{product_url}'"))

        # scrape download link
        try:
            download_link = self.driver.find_element(
                by=By.CSS_SELECTOR, value=CSS_SELECTOR_DOWNLOAD_LINK_GLOBAL
            ).get_attribute("href")
        except WebDriverException as e:
            try:
                download_link = self.driver.find_element(
                    by=By.CSS_SELECTOR, value=CSS_SELECTOR_DOWNLOAD_LINK_SIMPLE
                ).get_attribute("href")
            except:
                self.logger.debug(attribute_scraping_failure(f"download link for '{product_url}'"))

        self.logger.info(firmware_scraping_success(f"of {product_name} {product_url}"))
        return {
            "manufacturer": self.name,
            "product_name": product_name,
            "product_type": product_category,
            "version": version,
            "release_date": release_date,
            "checksum_scraped": None,
            "download_link": download_link,
            "additional_data": {},
        }

    def scrape_metadata(self) -> list[dict]:
        CSS_SELECTOR_CLOSE_SWITCH_REGION = "body > div.page-content-wrapper > div.tp-local-switcher > div > span"
        CSS_SELECTOR_PRODUCT_CATEGORIES = "#list > div.item"
        CSS_SELECTOR_PRODUCT_CATEGORIES_NAME = "h2 > span.tp-m-hide"
        CSS_SELECTOR_PRODUCT_LINKS = "div.item-box > span > a"

        self.logger.important(start_scraping())
        try:
            self.driver.get(self.scrape_entry_url)
            self.logger.info(entry_point_url_success(self.scrape_entry_url))
        except WebDriverException as e:
            self.logger.error(entry_point_url_failure(self.scrape_entry_url))
            self.logger.important(abort_scraping())
            return []

        # when first accessing the website, an overlay window asking to switch to the correct region might block other
        # elements; close this overlay
        try:
            self.driver.find_element(by=By.CSS_SELECTOR, value=CSS_SELECTOR_CLOSE_SWITCH_REGION).click()
        except WebDriverException as e:
            pass

        try:
            product_categories_el = self.driver.find_elements(by=By.CSS_SELECTOR, value=CSS_SELECTOR_PRODUCT_CATEGORIES)
        except WebDriverException as e:
            self.logger.error(f"Could not scrape product categories.\n{e}")
            self.logger.important(abort_scraping())
            return []

        product_categories = {}
        for category in product_categories_el:
            product_category_name = "unknown"
            try:
                product_category_name = category.find_element(
                    by=By.CSS_SELECTOR, value=CSS_SELECTOR_PRODUCT_CATEGORIES_NAME
                ).text
                product_category_name = self._clean_up_product_category(product_category_name)
                product_urls = [
                    el.get_attribute("href")
                    for el in category.find_elements(by=By.CSS_SELECTOR, value=CSS_SELECTOR_PRODUCT_LINKS)
                ]
                product_categories[product_category_name] = product_urls
            except WebDriverException as e:
                # self.logger.warning(f"Could not scrape URLs for product category '{product_category_name}'.")
                pass

        extracted_data = []
        for category in product_categories:
            if len(extracted_data) >= self.max_products:
                break
            for url in product_categories[category]:
                if product_metadata := self._scrape_product_metadata(url, category):
                    extracted_data.append(product_metadata)
                    if len(extracted_data) >= self.max_products:
                        break

        self.logger.important(finish_scraping())
        return extracted_data


if __name__ == "__main__":
    logger = get_logger()

    scraper = TPLinkScraper(logger, DOWNLOAD_URL_GLOBAL, max_products=50, headless=False)

    firmware_data = scraper.scrape_metadata()
    with open("../../../scraped_metadata/firmware_data_tp-link.json", "w") as firmware_file:
        json.dump(firmware_data, firmware_file)
