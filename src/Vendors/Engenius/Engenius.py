import time

from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.service import Service as ChromeService

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException

from loguru import logger as LOGGER

HOME_URL = "https://www.engeniusnetworks.eu/downloads/"
MANUFACTURER = "Engenius"
ignored_exceptions = (NoSuchElementException,
                      StaleElementReferenceException,
                      ElementNotInteractableException,
                      ElementClickInterceptedException)


class EngeniusScraper:
    def __init__(
        self,
        logger,
        scrape_entry_url: str = HOME_URL,
        headless: bool = True,
        max_products: int = float("inf")
    ):
        self.scrape_entry_url = scrape_entry_url
        self.logger = LOGGER
        self.max_products = max_products
        self.headless = headless
        self.name = MANUFACTURER
        self.__scrape_cnt = 0

        chromeOptions = webdriver.ChromeOptions()
        webdriver.ChromeOptions()

        if self.headless:
            chromeOptions.add_argument("--headless")

        chromeOptions.add_argument("--disable-dev-shm-using")
        chromeOptions.add_argument("--remote-debugging-port=9222")
        chromeOptions.add_argument("--start-maximized")

        self.driver = webdriver.Chrome(
            options=chromeOptions, service=ChromeService(ChromeDriverManager()
                                                         .install()))

    def _accept_cookies(self):
        SEL_COOKIE_ID = 'cn-accept-cookie'

        try:
            sel_accept_elem = self.driver.find_element(By.ID, SEL_COOKIE_ID)
            sel_accept_elem.click()
            self.logger.info('Accepted Cookies')
        except ignored_exceptions:
            self.logger.error('Failed to Accept Cookies')

    def _select_file_type(self):
        SEL_FIRMWARE_OPTION_XPATH = '//option[@value="firmware"]'

        try:
            sel_selector_elem = self.driver\
                .find_element(By.XPATH, SEL_FIRMWARE_OPTION_XPATH)
            sel_selector_elem.click()

            self.logger.info('Selected File Type -> Firmware')
        except ignored_exceptions:
            self.logger.error('Could not select File Type -> Firmware')

    def _get_category_elements(self) -> list:
        SEL_MENU_ID = "download-center-menu"
        SEL_CATEGORY_CLASS = "parent-list"

        try:
            sel_dl_menu = self.driver.find_element(By.ID, SEL_MENU_ID)

            sel_category_class = sel_dl_menu\
                .find_element(By.CLASS_NAME, SEL_CATEGORY_CLASS)

            sel_category_elements = sel_category_class\
                .find_elements(By.XPATH, "./*")

            self.logger.info("Categorys Found -> " +
                             str(len(sel_category_elements)))

        except ignored_exceptions:
            self.logger.error("Could not find any Categorys")
            return []

        return sel_category_elements

    def _scrape_product_metadata(self, product_name: str,
                                 category_name: str) -> list:
        SEL_DL_TABLE_ID = 'download-table'
        SEL_TABLE_BODY_TAG = 'tbody'

        product_metadata = []

        try:
            sel_dl_table_elem = self.driver\
                .find_element(By.ID, SEL_DL_TABLE_ID)

            sel_table_body_elem = sel_dl_table_elem\
                .find_element(By.TAG_NAME, SEL_TABLE_BODY_TAG)

            sel_file_elements = sel_table_body_elem\
                .find_elements(By.TAG_NAME, 'tr')

            for sel_file_elem in sel_file_elements:
                sel_file_content_elements = sel_file_elem\
                    .find_elements(By.TAG_NAME, 'td')

                if (sel_file_content_elements[0]
                        .get_attribute('innerHTML') == 'undefined'):
                    continue

                firmware_item = {
                    "manufacturer": MANUFACTURER,
                    "product_name": None,
                    "product_type": None,
                    "version": None,
                    "release_date": None,
                    "download_link": None,
                    "checksum_scraped": None,
                    "additional_data": {},
                }

                filename = sel_file_content_elements[0]\
                    .get_attribute('innerHTML')

                firmware_item["product_name"] = product_name
                firmware_item["product_type"] = category_name

                firmware_item["version"] = sel_file_content_elements[1]\
                    .get_attribute('innerHTML')

                firmware_item["release_date"] = sel_file_content_elements[4]\
                    .get_attribute('innerHTML')

                sel_link_elem = sel_file_content_elements[5]\
                    .find_element(By.TAG_NAME, 'a')

                firmware_item["download_link"] = sel_link_elem\
                    .get_attribute('href')

                product_metadata.append(firmware_item)

                self.logger.info('Firmware found -> (Category)' +
                                 category_name + ' -> (Product)' +
                                 product_name + ' -> (File Name)' +
                                 filename)
        except ignored_exceptions:
            self.logger.error(
                'Could not Scrape Product Metadata from Download Table')

        return product_metadata

    def _scrape_category_metadata(self, category_element) -> list:
        SEL_CHILD_LIST_CLASS = 'child-list'
        SEL_CATEGORY_NAME_CLASS = 'item-name'

        category_metadata = []

        time.sleep(2)

        try:
            WebDriverWait(self.driver, 100).until(
                expected_conditions.element_to_be_clickable(category_element))\
                .click()
        except ignored_exceptions:
            self.logger.error(
                'Failed to select Category')
            return []

        sel_category_name = category_element\
            .find_element(By.CLASS_NAME, SEL_CATEGORY_NAME_CLASS)

        category_name = sel_category_name.get_attribute('innerHTML')

        self.logger.info('Start Scraping Category -> ' + category_name)
        sel_product_list_elem = category_element\
            .find_element(By.CLASS_NAME, SEL_CHILD_LIST_CLASS)

        time.sleep(10)
        sel_product_elements = sel_product_list_elem\
            .find_elements(By.XPATH, './*')

        self.logger.info('Number of Products in ' + category_name +
                         ' -> ' + str(len(sel_product_elements)))

        for sel_product_elem in sel_product_elements:
            try:
                WebDriverWait(self.driver, 100).until(
                    expected_conditions.element_to_be_clickable(
                        sel_product_elem)).click()
            except ignored_exceptions:
                self.logger.error(
                    'Failed to Click to select Product in Category -> ' +
                    category_name)
                continue

            time.sleep(2)
            product_name = sel_product_elem.get_attribute('innerHTML')
            product_metadata = self._scrape_product_metadata(
                product_name, category_name)

            category_metadata = category_metadata + product_metadata

            if product_metadata:
                self.__scrape_cnt += 1

            if self.__scrape_cnt == self.max_products:
                return category_metadata

        return category_metadata

    def scrape_metadata(self) -> list:
        meta_data = []
        self.__scrape_cnt = 0

        try:
            self.driver.get(self.scrape_entry_url)
            self.logger.info(
                "Successfully accessed entry point URL " +
                self.scrape_entry_url)
        except ignored_exceptions as e:
            self.logger.error(
                "Abort scraping. Could not access entry point URL" + e)
            self.driver.quit()
            return []

        self._accept_cookies()
        self._select_file_type()

        sel_category_elements = self._get_category_elements()
        category_len = len(sel_category_elements)

        for i in range(0, category_len):
            category_metadata = self._scrape_category_metadata(
                sel_category_elements[i])

            meta_data = meta_data + category_metadata

            if self.__scrape_cnt == self.max_products:
                break

        self.logger.info('Done Scraping Engenius Firmware')
        self.logger.info('Total Engenius Firmware Scraped -> ' +
                         str(len(meta_data)))

        self.__scrape_cnt = 0
        self.driver.quit()

        return meta_data


def main():
    Scraper = EngeniusScraper(LOGGER, max_products=5)
    print(Scraper.scrape_metadata())


if __name__ == "__main__":
    main()
