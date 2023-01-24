import json

from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager

from src.logger import Logger
from src.logger_old import create_logger_old
from src.Vendors.scraper import Scraper

DOWNLOAD_URL = "https://dd-wrt.com/support/other-downloads/?path=betas"


class DDWRTScraper(Scraper):
    def __init__(
        self,
        logger,
        scrape_entry_url: str = DOWNLOAD_URL,
        headless: bool = True,
        max_products: int = float("inf"),
    ):
        self.name = "DDWRT"
        self.logger = Logger(self.name)
        self.scrape_entry_url = scrape_entry_url
        self.headless = headless
        self.max_products = max_products

        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        self.driver.implicitly_wait(0.5)  # has to be set only once

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

    def _scrape_product_metadata(self, product_name: str, product_url: str) -> list[dict]:
        CSS_SELECTOR_TABLE_ELEMENTS = "#dd_downloads > table > tbody > tr"
        CSS_SELECTOR_URL = "td:nth-child(1) > a"
        CSS_SELECTOR_ENTRY_TYPE = "td:nth-child(2)"
        CSS_SELECTOR_RELEASE_DATE = "td:nth-child(4)"

        product_metadata = []
        # sometimes product tables contain subdirectories with additional firmware
        # the url to these subdirectories is appended to the worklist to be scraped in the next iteration
        worklist = [product_url]

        while worklist:
            # access product page
            try:
                self.driver.get(worklist[0])
            except WebDriverException as e:
                self.logger.firmware_url_failure(product_url)
                return []

            table_entries = []
            try:
                table_entries = self.driver.find_elements(by=By.CSS_SELECTOR, value=CSS_SELECTOR_TABLE_ELEMENTS)
                # The first 3 elements from the table are not real products
                table_entries = table_entries[3:]
            except WebDriverException as e:
                self.logger.attribute_scraping_failure(f"download URLs for '{product_url}'")

            for i, entry in enumerate(table_entries):
                try:
                    entry_el = entry.find_element(by=By.CSS_SELECTOR, value=CSS_SELECTOR_URL)
                    entry_name = entry_el.text
                    # we exclude txt files from the scraped metadata
                    if ".txt" in entry_name:
                        continue
                    url = entry_el.get_attribute("href")
                except WebDriverException as e:
                    self.logger.attribute_scraping_failure(f"URL for entry {i} in table {product_url}")
                    return []

                try:
                    release_date = entry.find_element(by=By.CSS_SELECTOR, value=CSS_SELECTOR_RELEASE_DATE).text
                except WebDriverException as e:
                    release_date = None
                    self.logger.attribute_scraping_failure(f"release date for entry {i} in table {product_url}")

                try:
                    entry_type = entry.find_element(by=By.CSS_SELECTOR, value=CSS_SELECTOR_ENTRY_TYPE).text
                    if "DIR" in entry_type:
                        worklist.append(url)
                    else:
                        product_metadata.append(
                            {
                                "manufacturer": "DD-WRT",
                                "product_name": product_name,
                                # DD-WRT offers firmware for routers
                                "product_type": "Router",
                                # DD-WRT offers release dates instead of version numbers
                                "version": "NA",
                                "release_date": release_date,
                                "checksum_scraped": None,
                                "download_link": url,
                                "product_url": worklist[0],
                                "additional_data": {},
                            }
                        )
                        self.logger.firmware_scraping_success(f"{product_name} ({entry_name}) {worklist[0]}")
                except WebDriverException as e:
                    self.logger.attribute_scraping_failure(f"type for entry {i} in table {product_url}")

            worklist.pop(0)

        return product_metadata

    def _scrape_product_urls(self) -> list[tuple]:
        CSS_SELECTOR_PRODUCT_ELEMENTS = "#dd_downloads > table > tbody > tr"
        CSS_SELECTOR_PRODUCT_URL = "td > a"

        try:
            products = self.driver.find_elements(by=By.CSS_SELECTOR, value=CSS_SELECTOR_PRODUCT_ELEMENTS)
            # The first 3 elements from the table are not real products
            products = products[3:]
        except WebDriverException as e:
            self.logger.error(f"Could not scrape product URLs.\n{e}")
            self.logger.abort_scraping()
            return []

        product_urls = []
        for product in products[: self.max_products]:
            try:
                product_url_el = product.find_element(by=By.CSS_SELECTOR, value=CSS_SELECTOR_PRODUCT_URL)
                product_url = product_url_el.get_attribute("href")
                product_name = product_url_el.text
                product_urls.append((product_name, product_url))
            except WebDriverException:
                pass

        return product_urls

    def scrape_metadata(self) -> list[dict]:
        CSS_SELECTOR_COOKIE_CONSENT = (
            "#qc-cmp2-ui > div.qc-cmp2-footer.qc-cmp2-footer-overlay.qc-cmp2-footer-scrolled > div > button.css-47sehv"
        )
        CSS_SELECTOR_CURRENT_YEAR = "#dd_downloads > table > tbody > tr:last-child > td:nth-child(1) > a"
        CSS_SELECTOR_MOST_RECENT_REVISION = "#dd_downloads > table > tbody > tr:last-child > td:nth-child(1) > a"

        # self.logger.info(f"Start scraping metadata of firmware products.")
        self.logger.start_scraping()
        try:
            self.driver.get(self.scrape_entry_url)
            self.logger.entry_point_url_success(self.scrape_entry_url)
        except WebDriverException as e:
            self.logger.entry_point_url_failure(self.scrape_entry_url)
            return []

        # when first accessing the website, an overlay window asking to agree to a privacy policy might block other
        # elements; close this overlay
        try:
            self.driver.find_element(by=By.CSS_SELECTOR, value=CSS_SELECTOR_COOKIE_CONSENT).click()
        except WebDriverException as e:
            pass

        # to find current firmware versions, first the current year has to be selected from a list
        try:
            link_to_current_year = self.driver.find_element(
                by=By.CSS_SELECTOR, value=CSS_SELECTOR_CURRENT_YEAR
            ).get_attribute("href")
            self.driver.get(link_to_current_year)
        except WebDriverException as e:
            self.logger.error(f"Could not scrape most current firmware versions\n{e}")
            self.logger.abort_scraping()
            return []

        # to find current firmware versions for the selected year, the most recent revision has be selected from a list
        try:
            link_to_revision = self.driver.find_element(
                by=By.CSS_SELECTOR, value=CSS_SELECTOR_MOST_RECENT_REVISION
            ).get_attribute("href")
            self.driver.get(link_to_revision)
        except WebDriverException as e:
            self.logger.error(f"Could not scrape most current firmware versions\n{e}")
            self.logger.abort_scraping()
            return []

        product_urls = self._scrape_product_urls()

        extracted_data = []
        for tuple_ in product_urls:
            product_metadata = self._scrape_product_metadata(*tuple_)
            extracted_data.extend(product_metadata)

        self.logger.finish_scraping()
        return extracted_data


if __name__ == "__main__":
    # logger = create_logger(level="INFO")

    scraper = DDWRTScraper(None, DOWNLOAD_URL, max_products=50, headless=False)

    firmware_data = scraper.scrape_metadata()
    with open("../../../scraped_metadata/firmware_data_dd-wrt.json", "w") as firmware_file:
        json.dump(firmware_data, firmware_file)
