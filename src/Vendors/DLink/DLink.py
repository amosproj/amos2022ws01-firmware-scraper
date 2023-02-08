import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from src.Vendors.scraper import Scraper

from src.logger import *

HOME_URL = "https://tsd.dlink.com.tw/"
DOWNLOAD_URL = "https://tsd.dlink.com.tw/ddgo"
MANUFACTURER = "DLink"
ignored_exceptions = (Exception)


class DLinkScraper(Scraper):
    def __init__(
        self,
        driver,
        scrape_entry_url: str = HOME_URL,
        headless: bool = True,
        max_products: int = float("inf")
    ):
        self.scrape_entry_url = scrape_entry_url
        self.logger = get_logger()
        self.max_products = max_products
        self.headless = headless
        self.name = MANUFACTURER
        self.__scrape_cnt = 0
        self.__meta_data = []

        self.driver = driver

    def __get_product_selectors(self) -> list:
        SEL_PRODUCT_TABLE_XPATH =\
            '/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table[2]/tbody'
        sel_products = []
        try:
            sel_product_table = self.driver.find_element(
                By.XPATH,
                SEL_PRODUCT_TABLE_XPATH
            )
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
            self.logger.debug('Failed to find Firmware Table')

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
                By.XPATH,
                SEL_HEADER_XPATH
            ).get_attribute('innerHTML')

            sel_table = self.driver.find_element(By.XPATH, SEL_TABLE_XPATH)
            sel_rows = sel_table.find_elements(By.XPATH, './*')

            if len(sel_rows) < 4:
                self.logger.debug(
                    'Could not extract Metadata from Firmware Table'
                )
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
                self.logger.warning("Could not find Download Link")
                self.driver.execute_script("window.history.go(-1)")
                return None
            else:
                firmware_item["download_link"] = download_links[1]\
                    .get_attribute('href')

        except ignored_exceptions:
            self.logger.warning(
                'Could not extract Metadata from Firmware Table'
            )
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
                self.logger.debug("Could not Get Firmware Rows, Wrong row amt")
                continue

            try:
                file_type = sel_rows[i].find_elements(
                    By.XPATH,
                    './*'
                )[0].get_attribute('innerHTML')

                if file_type != 'Firmware':
                    continue

                sel_rows[i].click()
                extracted_data = self.__extract_metadata_from_table()

                if not extracted_data:
                    continue

                extracted_data["product_type"] = category_name
                self.__scrape_cnt = self.__scrape_cnt + 1
                self.__meta_data.append(extracted_data)

                self.logger.info(
                    firmware_scraping_success(
                        f"{extracted_data['product_name']} {extracted_data['download_link']}"
                    )
                )

                if self.__scrape_cnt == self.max_products:
                    self.logger.debug(
                        'Successfully Scraped Max Products Firmware Amount -> '
                        + str(self.max_products)
                    )
                    self.driver.refresh()
                    return
            except ignored_exceptions:
                self.logger.debug('Could not click on selected Firmware')
                continue

        self.driver.execute_script("window.history.go(-1)")

    def _loop_products(self, category_name: str):
        sel_products = self.__get_product_selectors()

        try:
            sel_first_row = sel_products[0].find_element(
                By.CLASS_NAME,
                'pord_3'
            )

            if sel_first_row.find_element(By.TAG_NAME, 'a')\
                    .get_attribute('title') == 'N/A':
                self.logger.debug(
                    'Products in (Category)' +
                    category_name + ' Found -> 0'
                )
                return
        except ignored_exceptions:
            self.logger.warning('Could not analyze Products in Category')
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
                self.logger.warning('Could not Click on Product')
                continue

            self._scrape_product_firmware(category_name)

            if self.__scrape_cnt == self.max_products:
                return

        sel_products = self.__get_product_selectors()

        """Recursive Loop Products, until there are no next pages"""
        if len(sel_products) == product_amt:
            sel_next_xpath = '//a[@href="javascript:go(\'N\')"]'
            try:
                self.driver.refresh()
                time.sleep(2)
                next_page = self.driver.find_element(
                    By.XPATH,
                    sel_next_xpath
                )

                next_page.click()
                time.sleep(2)
                self._loop_products(category_name)
                time.sleep(2)
            except ignored_exceptions:
                self.logger.debug(
                    "Scraped all Products from Category -> "
                    + category_name
                )

        self.driver.execute_script("window.history.go(-1)")
        time.sleep(2)

    def __get_category_selectors(self) -> list:
        SEL_CAT_TABLE_XPATH = '/html/body/form/table[3]/tbody/tr/td[1]/table[2]/tbody'

        try:
            sel_cat_table = self.driver.find_element(
                By.XPATH,
                SEL_CAT_TABLE_XPATH
            )

            sel_cat_selectors = sel_cat_table.find_elements(By.TAG_NAME, 'tr')
        except ignored_exceptions:
            self.logger.warning('Could not find Category Table')
            return []

        return sel_cat_selectors

    def _loop_categorys(self):
        sel_cat_selectors = self.__get_category_selectors()
        cat_amt = len(sel_cat_selectors)

        self.logger.debug(
            "Categorys Found -> " +
            str(len(sel_cat_selectors))
        )

        for i in range(1, cat_amt-1):
            try:
                sel_cat_selectors = self.__get_category_selectors()
                sel_product_selector = sel_cat_selectors[i].find_element(
                    By.TAG_NAME,
                    'a'
                )

                category_name = sel_product_selector.get_attribute('innerHTML')
                time.sleep(2)

                WebDriverWait(self.driver, 1000).until(
                    EC.element_to_be_clickable(sel_product_selector))\
                    .click()

                self.logger.debug('Select -> (Category)' + category_name)
            except ignored_exceptions:
                self.logger.warning('Could not click on Category')
                continue

            self._loop_products(category_name)

            if self.__scrape_cnt == self.max_products:
                return

    def __get_type_selector(self):
        TYPE_SELECTOR = '//select[@name="ModelCategory_home"]'

        try:
            type_sel = self.driver.find_element(
                By.XPATH,
                TYPE_SELECTOR
            )

            return type_sel
        except Exception:
            self.logger.warning("Could not get Type Selector Element")

        return None

    def __get_model_selector(self):
        MODEL_SELECTOR = '//select[@name="ModelSno_home"]'

        try:
            model_sel = self.driver.find_element(
                By.XPATH,
                MODEL_SELECTOR
            )

            return model_sel
        except Exception:
            self.logger.warning("Could not get Model Selector Element")

        return None

    def scrape_without_category(self):
        try:
            type_sel = self.__get_type_selector()
            type_options = type_sel.find_elements(By.TAG_NAME, 'option')
            type_amt = len(type_options)
        except Exception:
            self.logger.error("Could not Find Type Selector")

        for i in range(1, type_amt):
            try:
                # Get Product Type Options
                type_sel = self.__get_type_selector()
                type_options = type_sel.find_elements(By.TAG_NAME, 'option')

                # Get Name of Product Type
                option_type_name = type_options[i].get_attribute('value')

                # Select Product Type
                type_select = Select(type_sel)
                type_select.select_by_visible_text(option_type_name)

                # Get Model Options Amount
                model_sel = self.__get_model_selector()
                model_options = model_sel.find_elements(By.TAG_NAME, 'option')
                model_amt = len(model_options)
            except Exception:
                self.logger.debug("Could not Select Product Type")
                continue

            for j in range(1, model_amt):
                try:
                    # Get Product Model Options
                    model_sel = self.__get_model_selector()
                    model_options = model_sel.find_elements(
                        By.TAG_NAME,
                        'option'
                    )

                    # Get Name of Product Model
                    option_model_name = model_options[j].get_attribute('value')

                    # Select Product Model
                    model_select = Select(model_sel)
                    model_select.select_by_visible_text(option_model_name)

                    # Enter Selection
                    self.driver.execute_script("javascript:s1(document.form1)")

                    self._scrape_product_firmware(option_type_name)
                except Exception:
                    self.logger.debug("Could not Select Model Type")
                    continue

                if self.__scrape_cnt == self.max_products:
                    return

                time.sleep(1)

    def download_firmware(self, links: list):
        try:
            type_sel = self.__get_type_selector()
            type_select = Select(type_sel)
            type_select.select_by_visible_text('ANT24')

            model_sel = self.__get_model_selector()
            model_select = Select(model_sel)
            model_select.select_by_visible_text('0501')

            self.driver.execute_script("javascript:s1(document.form1)")
            self.driver.execute_script("dwn('EFFGEIGEJH','1')")

            self.logger.important(firmware_url_success(DOWNLOAD_URL))
        except ignored_exceptions:
            self.logger.error(firmware_scraping_failure(DOWNLOAD_URL))
            self.driver.quit()
            return []

        for link in links:
            self.logger.info("Download Firmware -> " + link[1])
            self.driver.execute_script(link[1])

        self.driver.quit()

    def scrape_metadata(self) -> list:
        meta_data = []
        self.__scrape_cnt = 0
        self.__meta_data = []

        self.logger.important(start_scraping())
        self.logger.debug('Headless -> ' + str(self.headless))
        self.logger.debug(
            'Max Products to Scrape -> ' +
            str(self.max_products)
        )

        try:
            self.driver.get(self.scrape_entry_url)
            self.logger.important(firmware_url_success(self.scrape_entry_url))
        except ignored_exceptions:
            self.logger.error(firmware_scraping_failure(self.scrape_entry_url))
            self.driver.quit()
            return []

        time.sleep(5)

        '''Function Loop Categorys doesnt work properly'''
        # self._loop_categorys()

        self.scrape_without_category()

        meta_data = self.__meta_data

        self.logger.debug('Metadata Found -> ' + str(len(meta_data)))
        self.logger.important(finish_scraping())

        self.__scrape_cnt = 0
        self.__meta_data = []

        self.driver.quit()

        return meta_data


if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    options = Options()
    options.add_argument("--headless")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    Scraper = DLinkScraper(headless=True, max_products=1000, driver=driver)
    meta_data = Scraper.scrape_metadata()
    with open("scraped_metadata/firmware_data_DLink.json", "w") as firmware_file:
        json.dump(meta_data, firmware_file)
