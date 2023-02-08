import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from src.logger import *
from src.Vendors.scraper import Scraper

HOME_URL = "https://www.engeniusnetworks.eu/downloads/"
MANUFACTURER = "Engenius"
ignored_exceptions = (Exception)


class EngeniusScraper(Scraper):
    def __init__(
        self,
        driver,
        scrape_entry_url: str = HOME_URL,
        headless: bool = True,
        max_products: int = float("inf")
    ):
        self.scrape_entry_url = scrape_entry_url
        self.name = MANUFACTURER
        self.logger = get_logger()
        self.max_products = max_products
        self.headless = headless
        self.__scrape_cnt = 0
        self.driver = driver

    def _accept_cookies(self):
        SEL_COOKIE_ID = 'cn-accept-cookie'

        try:
            sel_accept_elem = self.driver.find_element(By.ID, SEL_COOKIE_ID)
            sel_accept_elem.click()
            self.logger.debug('Accepted Cookies')
        except ignored_exceptions:
            self.logger.error('Failed to Accept Cookies')

    def _select_file_type(self):
        SEL_FIRMWARE_OPTION_XPATH = '//option[@value="firmware"]'

        try:
            sel_selector_elem = self.driver.find_element(
                By.XPATH,
                SEL_FIRMWARE_OPTION_XPATH
            )

            sel_selector_elem.click()
        except ignored_exceptions:
            self.logger.error('Could not select File Type -> Firmware')

    def _get_category_elements(self) -> list:
        SEL_MENU_ID = "download-center-menu"
        SEL_CATEGORY_CLASS = "parent-list"

        try:
            sel_dl_menu = self.driver.find_element(By.ID, SEL_MENU_ID)

            sel_category_class = sel_dl_menu.find_element(
                By.CLASS_NAME,
                SEL_CATEGORY_CLASS
            )

            sel_category_elements = sel_category_class.find_elements(
                By.XPATH,
                "./*"
            )

            self.logger.debug(
                "Categorys Found -> " +
                str(len(sel_category_elements))
            )

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
            sel_dl_table_elem = self.driver.find_element(
                By.ID,
                SEL_DL_TABLE_ID
            )

            sel_table_body_elem = sel_dl_table_elem.find_element(
                By.TAG_NAME,
                SEL_TABLE_BODY_TAG
            )

            sel_file_elements = sel_table_body_elem.find_elements(
                By.TAG_NAME,
                'tr'
            )
        except ignored_exceptions:
            self.logger.warning(
                'Could not find Download Table'
            )
            return []

        for sel_file_elem in sel_file_elements:
            try:
                sel_file_content_elements = sel_file_elem.find_elements(
                    By.TAG_NAME,
                    'td'
                )
                time.sleep(1)
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

                # filename = sel_file_content_elements[0].get_attribute(
                #    'innerHTML'
                # )

                firmware_item["product_name"] = product_name
                firmware_item["product_type"] = category_name

                firmware_item["version"] = sel_file_content_elements[1]\
                    .get_attribute('innerHTML')

                time.sleep(1)

                firmware_item["release_date"] = sel_file_content_elements[4]\
                    .get_attribute('innerHTML')

                time.sleep(1)

                sel_link_elem = sel_file_content_elements[5]\
                    .find_element(By.TAG_NAME, 'a')

                time.sleep(1)

                firmware_item["download_link"] = sel_link_elem\
                    .get_attribute('href')

                product_metadata.append(firmware_item)

                self.logger.info(
                    firmware_scraping_success(
                        f"{firmware_item['product_name']} {firmware_item['download_link']}"
                    )
                )
            except ignored_exceptions:
                self.logger.warning(
                    'Could not Scrape Product Metadata from Download Table'
                )
                continue

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
            self.logger.warning(
                'Failed to select Category'
            )
            return []

        sel_category_name = category_element.find_element(
            By.CLASS_NAME,
            SEL_CATEGORY_NAME_CLASS
        )

        category_name = sel_category_name.get_attribute('innerHTML')

        self.logger.debug('Start Scraping Category -> ' + category_name)
        sel_product_list_elem = category_element.find_element(
            By.CLASS_NAME,
            SEL_CHILD_LIST_CLASS
        )

        time.sleep(10)
        sel_product_elements = sel_product_list_elem.find_elements(
            By.XPATH,
            './*'
        )

        self.logger.debug(
            'Number of Products in '
            + category_name
            + ' -> '
            + str(len(sel_product_elements))
        )

        for sel_product_elem in sel_product_elements:
            try:
                WebDriverWait(self.driver, 100).until(
                    expected_conditions.element_to_be_clickable(
                        sel_product_elem)).click()
            except ignored_exceptions:
                self.logger.warning(
                    'Failed to Click to select Product in Category -> '
                    + category_name
                )
                continue

            time.sleep(2)
            product_name = sel_product_elem.get_attribute('innerHTML')
            product_metadata = self._scrape_product_metadata(
                product_name,
                category_name
            )

            category_metadata = category_metadata + product_metadata

            if product_metadata:
                self.__scrape_cnt += 1

            if self.__scrape_cnt == self.max_products:
                return category_metadata

        return category_metadata
    
    def download_firmware(self, links:list):
        for link in links:
            self.logger.info("Download Firmware -> " + link[1])
            self.driver.get(link[1])

    def scrape_metadata(self) -> list:
        meta_data = []
        self.__scrape_cnt = 0

        self.logger.important(start_scraping())
        self.logger.debug('Headless -> ' + str(self.headless))

        self.logger.debug(
            'Max Products to Scrape -> '
            + str(self.max_products)
        )

        try:
            self.driver.get(self.scrape_entry_url)
            self.logger.important(firmware_url_success(self.scrape_entry_url))
        except ignored_exceptions:
            self.logger.error(firmware_scraping_failure(self.scrape_entry_url))
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

        self.logger.debug('Metadata Found -> ' + str(len(meta_data)))
        self.logger.important(finish_scraping())

        self.__scrape_cnt = 0
        self.driver.quit()

        return meta_data


if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    options = Options()
    # options.add_argument("--headless")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    Scraper = EngeniusScraper(headless=False, max_products=50, driver=driver)
    metadata = Scraper.scrape_metadata()
    with open("scraped_metadata/firmware_data_Engenius.json", "w") as firmware_file:
        json.dump(metadata, firmware_file)
