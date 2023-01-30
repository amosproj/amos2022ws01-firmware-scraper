import json
import time

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from src.logger import * 
from src.Vendors.scraper import Scraper
HOME_URL = "https://library.abb.com/r?dkg=dkg_software&q=firmware"
MANUFACTURER = "ABB"
ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)


class ABBScraper(Scraper):
    def __init__(
        self,
        driver,
        scrape_entry_url: str = HOME_URL,
        headless: bool = True,
        max_products: int = float("inf")
    ):
        self.scrape_entry_url = scrape_entry_url
        self.max_products = max_products
        self.name = MANUFACTURER
        self.__scrape_cnt = 0
        self.headless = headless
        self.logger = get_logger()
        self.driver = driver

    def _accept_cookies(self):
        SEL_BTN_XPATH =\
            '//button[@data-locator="privacy-notice-confirmation-accept-btn"]'

        time.sleep(5)
        try:
            accept_btn = self.driver\
                .find_element(By.XPATH,
                              SEL_BTN_XPATH)
            accept_btn.click()
            self.logger.important('Successfully Accepted Cookies')
        except Exception as e:
            self.logger.error('Could not Accept Cookies -> ' + str(e))
        time.sleep(5)

    def _navigate_to_category(self):
        time.sleep(3)

        try:
            btn = WebDriverWait(self.driver, 10, ignored_exceptions=ignored_exceptions)\
                .until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                        '//*[@id="app"]/div/div/div[2]/div[2]/div[1]/div/div/div/div[1]/button')))

            time.sleep(3)
            btn.click()
            time.sleep(1)
            inner_btn = self.driver.find_element(
                By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div[1]/div/div/div/div[2]/div/div/div/div[1]/button')
            inner_btn.click()
        except Exception as e:
            self.logger.error('Could not Navigate to Category -> ' + str(e))

    def _click_category_button(self, id: int) -> str:
        try:
            children = self.driver.find_element(
                By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div[1]/div/div/div/div[2]/div/div/div/div/div')
            time.sleep(1)
            nav = children.find_elements(By.CLASS_NAME, 'sc-hBEYId')

            # get name of category
            cat_name = nav[id].find_element(
                By.TAG_NAME, 'span').get_attribute('innerHTML').lstrip()

            # show sub categorys
            btn = WebDriverWait(nav[id], 10, ignored_exceptions=ignored_exceptions)\
                .until(expected_conditions.presence_of_element_located((By.TAG_NAME, "button")))
            btn.click()
        except Exception as e:
            self.logger.error('Could not Click Category Button -> ' + str(e))
            return ""

        time.sleep(3)

        return cat_name

    def _scrape_category_data(self, cat_name: str) -> list:
        meta_data = []
        try:
            name = self.driver.find_elements(
                By.XPATH, '//div[@data-locator="search-result-row"]')
            dates = self.driver.find_elements(
                By.XPATH, '//div[@data-locator="search-result-published-date"]')
            links = self.driver.find_elements(
                By.XPATH, '//a[@data-locator="search-result-row-link"]')
            file_names = self.driver.find_elements(
                By.XPATH, '//div[@data-locator="search-result-title"]')

            if not len(name) == len(dates) == len(links) == len(file_names):
                self.logger.error('Could not find Firmware -> (Category)'
                                  + cat_name)
                return []
        except Exception as e:
            self.logger.error('Could not find Firmware -> (Category)'
                              + cat_name
                              + " -> "
                              + str(e))
            return []

        for i in range(0, len(name)):
            firmware_item = {
                "manufacturer": "ABB",
                "product_name": None,
                "product_type": None,
                "version": None,
                "release_date": None,
                "download_link": None,
                "checksum_scraped": None,
                "additional_data": {},
            }

            try:
                firmware_item["product_name"] = file_names[i].get_attribute(
                    'innerHTML')
                firmware_item["product_type"] = cat_name
                firmware_item["release_date"] = dates[i].get_attribute(
                    'innerHTML')
                firmware_item["download_link"] = links[i].get_attribute('href')
            except Exception as e:
                self.logger\
                    .error('Could not Scrape Firmware. Skip Firmware -> '
                           + str(e))
                continue

            meta_data.append(firmware_item)
            self.__scrape_cnt += 1

            if self.__scrape_cnt == self.max_products:
                break

        return meta_data

    def scrape_metadata(self) -> list:
        try:
            self.driver.get(self.scrape_entry_url)
            self.driver.maximize_window()
            self.logger.important(
                "Successfully accessed entry point URL " +
                self.scrape_entry_url)
        except ignored_exceptions as e:
            self.logger.error(
                "Abort scraping. Could not access entry point URL -> "
                + str(e))
            self.driver.quit()
            return []

        self._accept_cookies()
        self._navigate_to_category()

        try:
            # get child categorys
            cat = self.driver.find_element(
                By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div[1]/div/div/div/div[2]/div/div/div/div/div')
            nav = cat.find_elements(
                By.XPATH, '//div[@data-locator="category"]')
            time.sleep(1)
        except Exception as e:
            self.logger\
                .error('Abort Scraping. Could not get Child Category -> '
                       + str(e))
            return []

        nav_len = len(nav)

        meta_data = []
        for i in range(0, nav_len):
            cat_name = self._click_category_button(i)
            if not cat_name:
                continue

            category_data = self._scrape_category_data(cat_name)
            meta_data = meta_data + category_data
            self.driver.execute_script("window.history.go(-1)")

            if self.__scrape_cnt == self.max_products:
                self.logger.important('Successfully Scraped Max Products -> '
                                    + str(self.max_products))
                break

        self.driver.quit()

        self.logger.important(
            'Successfully Scraped ABB Firmware -> ' + str(len(meta_data)))
        self.logger.info('Done.')

        return meta_data


if __name__ == "__main__":
    Scraper = ABBScraper(logger=get_logger(), headless=True)
    meta_data = Scraper.scrape_metadata()
    with open("scraped_metadata/firmware_data_ABB.json", "w") as firmware_file:
        json.dump(meta_data, firmware_file)
