from re import A, X
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import selenium
import json
import time
import requests
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

HOME_URL = "https://library.abb.com/r?dkg=dkg_software&q=firmware"
MANUFACTURER = "ABB"
ignored_exceptions=(NoSuchElementException,StaleElementReferenceException)

class ABBScraper:
    def __init__(
            self,
            logger,
            scrape_entry_url: str = HOME_URL,
            headless: bool = True,
            max_products: int = float("inf")
        ):
        self.vendor_url = scrape_entry_url
        self.max_products = max_products
        self.name = MANUFACTURER
        self.__scrape_cnt = 0
        self.headless = headless
        chromeOptions = webdriver.ChromeOptions() 
        webdriver.ChromeOptions()


        if self.headless:
            chromeOptions.add_argument("--headless")

        chromeOptions.add_argument("--disable-dev-shm-using") 
        chromeOptions.add_argument("--remote-debugging-port=9222")

        self.driver = webdriver.Chrome(options=chromeOptions, service=ChromeService(ChromeDriverManager().install()))
        
    def _accept_cookies(self):
        self.driver.get(self.vendor_url)
        self.driver.maximize_window()

        time.sleep(5)
        accept_btn = self.driver.find_element(By.XPATH, '//button[@data-locator="privacy-notice-confirmation-accept-btn"]')
        accept_btn.click()

    def _navigate_to_category(self):
        time.sleep(3)
        btn = WebDriverWait(self.driver, 10, ignored_exceptions=ignored_exceptions)\
                        .until(expected_conditions.presence_of_element_located((By.XPATH, 
                        '//*[@id="app"]/div/div/div[2]/div[2]/div[1]/div/div/div/div[1]/button')))

        time.sleep(3)                
        btn.click()
        time.sleep(1)
        inner_btn = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div[1]/div/div/div/div[2]/div/div/div/div[1]/button')
        inner_btn.click()

    def _click_category_button(self, id: int) -> str:
        children = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div[1]/div/div/div/div[2]/div/div/div/div/div')
        time.sleep(1)
        nav = children.find_elements(By.CLASS_NAME, 'sc-hBEYId')

        #get name of category
        cat_name = nav[id].find_element(By.TAG_NAME, 'span').get_attribute('innerHTML').lstrip()

        #show sub categorys
        btn = WebDriverWait(nav[id], 10, ignored_exceptions=ignored_exceptions)\
                    .until(expected_conditions.presence_of_element_located((By.TAG_NAME, "button")))
        btn.click()
        
        time.sleep(3)

        return cat_name

    def _scrape_category_data(self, cat_name: str) -> list:
        meta_data = []

        name = self.driver.find_elements(By.XPATH, '//div[@data-locator="search-result-row"]')
        dates = self.driver.find_elements(By.XPATH, '//div[@data-locator="search-result-published-date"]')
        links = self.driver.find_elements(By.XPATH, '//a[@data-locator="search-result-row-link"]')
        file_names = self.driver.find_elements(By.XPATH, '//div[@data-locator="search-result-title"]')

        if not len(name) == len(dates) == len(links) == len(file_names):
            print("FEHLER")

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

            firmware_item["product_name"] = file_names[i].get_attribute('innerHTML')
            firmware_item["product_type"] = cat_name
            firmware_item["release_date"] = dates[i].get_attribute('innerHTML')
            firmware_item["download_link"] = links[i].get_attribute('href')

            meta_data.append(firmware_item)
            self.__scrape_cnt += 1

            if self.__scrape_cnt == self.max_products:
                break

        return meta_data


    def scrape_metadata(self) -> list:
        self._accept_cookies()
        self._navigate_to_category()

        #get child categorys
        cat= self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div[1]/div/div/div/div[2]/div/div/div/div/div')
        nav = cat.find_elements(By.XPATH, '//div[@data-locator="category"]')
        time.sleep(1)

        nav_len = len(nav)

        meta_data = []
        for i in range(0, nav_len):
            cat_name = self._click_category_button(i)
            category_data = self._scrape_category_data(cat_name)
            meta_data = meta_data + category_data
            self.driver.execute_script("window.history.go(-1)")

            if self.__scrape_cnt == self.max_products:
                break

        self.driver.quit()
        
        return meta_data

def main():
    Scraper = ABBScraper(max_products=10, logger=None, headless=False)
    meta_data = Scraper.scrape_metadata()
    print(meta_data)

if __name__ == "__main__":
    main()