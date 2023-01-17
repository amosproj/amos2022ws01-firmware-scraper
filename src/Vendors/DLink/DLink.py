import time
import json
from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException

from loguru import logger as LOGGER

HOME_URL = "https://tsd.dlink.com.tw/"
MANUFACTURER = "DLink"
ignored_exceptions = (NoSuchElementException,
                      StaleElementReferenceException,
                      ElementNotInteractableException,
                      ElementClickInterceptedException)


class DLinkScraper:
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
        self.__meta_data = []

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

    def __get_product_selectors(self) -> list:
        SEL_PRODUCT_TABLE_XPATH =\
            '/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table[2]/tbody'
        sel_products = []
        try:
            sel_product_table = self.driver.find_element(
                By.XPATH, SEL_PRODUCT_TABLE_XPATH)
            sel_products = sel_product_table.find_elements(By.XPATH, './*')
        except ignored_exceptions:
            self.logger.error('Could not find Product Table')

        return sel_products

    def __get_firmware_rows(self) -> list:
        sel_rows = []
        try:
            time.sleep(1)
            sel_rows = self.driver.find_elements(By.ID, 'rsq')
        except ignored_exceptions:
            self.logger.error('Failed to find Firmware Table')

        return sel_rows

    def __convert_date(self, to_convert: str) -> str:
        converted = to_convert.replace('/', '-')
        return converted

    def __extract_metadata_from_table(self) -> dict:
        SEL_HEADER_XPATH = '/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr/td/big/strong'
        SEL_TABLE_XPATH = '/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr/td/table/tbody'

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

        try:
            product_name = self.driver.find_element(
                By.XPATH, SEL_HEADER_XPATH).get_attribute('innerHTML')

            sel_table = self.driver.find_element(By.XPATH, SEL_TABLE_XPATH)
            sel_rows = sel_table.find_elements(By.XPATH, './*')

            if len(sel_rows) < 4:
                self.logger.error(
                    'Could not extract Metadata from Firmware Table')
                self.driver.execute_script("window.history.go(-1)")
                return None

            firmware_item["product_name"] = product_name
            firmware_item["product_type"] = None

            firmware_item["version"] = sel_rows[1]\
                .find_element(By.CLASS_NAME, 'MdDclist12')\
                .get_attribute('innerHTML')\
                .strip()

            release_date = sel_rows[3]\
                .find_element(By.CLASS_NAME, 'MdDclist12')\
                .get_attribute('innerHTML')\
                .strip()

            firmware_item["release_date"] = self.__convert_date(release_date)

            download_links = sel_rows[2]\
                .find_element(By.CLASS_NAME, 'MdDclist12')\
                .find_elements(By.TAG_NAME, 'a')

            if len(download_links) == 1:
                firmware_item["download_link"] = download_links[0]\
                    .get_attribute('href')
            elif len(download_links) < 2:
                self.logger.error("Could not find Download Link")
                self.driver.execute_script("window.history.go(-1)")
                return None
            else:
                firmware_item["download_link"] = download_links[1]\
                    .get_attribute('href')

        except ignored_exceptions:
            self.logger.error('Could not extract Metadata from Firmware Table')
            self.driver.execute_script("window.history.go(-1)")
            return None

        self.driver.execute_script("window.history.go(-1)")

        return firmware_item

    def _scrape_product_firmware(self, category_name: str):
        sel_rows = self.__get_firmware_rows()
        row_amt = len(sel_rows)

        for i in range(0, row_amt):
            sel_rows = self.__get_firmware_rows()

            if len(sel_rows) != row_amt:
                self.logger.error("Could not Get Firmware Rows, Wrong row amt")
                continue

            try:
                file_type = sel_rows[i].find_elements(
                    By.XPATH, './*')[0].get_attribute('innerHTML')

                if file_type != 'Firmware':
                    continue

                sel_rows[i].click()
                extracted_data = self.__extract_metadata_from_table()

                if not extracted_data:
                    continue

                extracted_data["product_type"] = category_name
                self.__scrape_cnt = self.__scrape_cnt + 1
                self.__meta_data.append(extracted_data)

                if self.__scrape_cnt == self.max_products:
                    self.logger.info(
                        'Successfully Scraped Max Products Firmware Amount -> '
                        + str(self.max_products))
                    break
            except ignored_exceptions:
                self.logger.error('Could not click on selected Firmware')
                continue

        self.driver.execute_script("window.history.go(-1)")

    def _loop_products(self, category_name: str):
        sel_products = self.__get_product_selectors()

        try:
            sel_first_row = sel_products[0].find_element(
                By.CLASS_NAME, 'pord_3')

            if sel_first_row.find_element(By.TAG_NAME, 'a').get_attribute('title') == 'N/A':
                self.logger.info('Products in (Category)' +
                                 category_name + ' Found -> 0')
                return
        except ignored_exceptions:
            self.logger.error('Could not analyze Products in Category')
            return

        product_amt = len(sel_products)

        for i in range(1, product_amt-2):
            sel_products = self.__get_product_selectors()

            try:
                sel_products[i]\
                    .find_element(By.CLASS_NAME, 'pord_3')\
                    .find_element(By.TAG_NAME, 'a')\
                    .click()
            except ignored_exceptions:
                self.logger.error('Could not Click on Product')
                continue

            self._scrape_product_firmware(category_name)

            if self.__scrape_cnt == self.max_products:
                break

        sel_products = self.__get_product_selectors()

        """Recursive Loop Products, until there are no next pages"""
        if len(sel_products) == product_amt:
            sel_next_xpath = '//a[@href="javascript:go(\'N\')"]'
            try:
                self.driver.refresh()
                next_page = self.driver\
                    .find_element(By.XPATH, sel_next_xpath)

                next_page.click()
                time.sleep(2)
                self._loop_products(category_name)
                time.sleep(1)
            except ignored_exceptions:
                self.logger.info(
                    "Scraped all Products from Category -> " + category_name)

        self.driver.execute_script("window.history.go(-1)")

    def __get_category_selectors(self) -> list:
        SEL_CAT_TABLE_XPATH = '/html/body/form/table[3]/tbody/tr/td[1]/table[2]/tbody'

        try:
            sel_cat_table = self.driver.find_element(
                By.XPATH, SEL_CAT_TABLE_XPATH)

            sel_cat_selectors = sel_cat_table.find_elements(By.TAG_NAME, 'tr')
        except ignored_exceptions:
            self.logger.error('Could not find Category Table')
            return []

        return sel_cat_selectors

    def _loop_categorys(self):
        sel_cat_selectors = self.__get_category_selectors()
        cat_amt = len(sel_cat_selectors)

        self.logger.info("Categorys Found -> " +
                         str(len(sel_cat_selectors)))

        for i in range(1, cat_amt-1):
            try:
                sel_cat_selectors = self.__get_category_selectors()
                sel_product_selector = sel_cat_selectors[i].find_element(
                    By.TAG_NAME, 'a')

                category_name = sel_product_selector.get_attribute('innerHTML')
                time.sleep(2)

                WebDriverWait(self.driver, 1000).until(
                    EC.element_to_be_clickable(sel_product_selector))\
                    .click()

                self.logger.info('Select -> (Category)' + category_name)
            except ignored_exceptions:
                self.logger.error('Could not click on Category')
                continue

            self._loop_products(category_name)

            if self.__scrape_cnt == self.max_products:
                break

    def download_link(self, links: list):
        try:
            self.driver.get(self.scrape_entry_url)
            self.logger.info(
                "Successfully accessed entry point URL " +
                self.scrape_entry_url)
        except ignored_exceptions as e:
            self.logger.error(
                "Abort Downloading. Could not access entry point URL" + e)
            self.driver.quit()
            return []

        for link in links:
            self.logger.info("Download Firmware -> " + link["product_name"])
            self.driver.execute_script(link["download_link"])

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

        time.sleep(10)
        self._loop_categorys()

        meta_data = self.__meta_data
        self.logger.info('Done Scraping DLink Firmware')
        self.logger.info('Total DLink Firmware Scraped -> ' +
                         str(len(meta_data)))

        self.__scrape_cnt = 0
        self.__meta_data = []

        self.driver.quit()

        return meta_data


def main():
    Scraper = DLinkScraper(LOGGER, headless=False, max_products=10)
    meta_data = Scraper.scrape_metadata()
    json_data = json.dumps(meta_data)
    print(json_data)


if __name__ == "__main__":
    main()
