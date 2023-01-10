from re import A, X
from unicodedata import category
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import selenium
import time
import requests
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.service import Service as ChromeService

import json

HOME_URL = "https://www.trendnet.com/support/"
MANUFACTURER = "Trendnet"
DOWNLOAD_BASE_LINK = "https://www.trendnet.com/asp/download_manager/inc_downloading.asp?button=Continue+with+Download&Continue=yes&iFile="

class TrendnetScraper:
    def __init__(
            self,
            logger,
            scrape_entry_url: str = HOME_URL,
            headless: bool = True,
            max_products: int = float("inf")
        ):
        self.name = MANUFACTURER
        self.vendor_url = scrape_entry_url
        chromeOptions = webdriver.ChromeOptions() 
        webdriver.ChromeOptions()
        chromeOptions.add_argument("--disable-dev-shm-using") 
        chromeOptions.add_argument("--remote-debugging-port=9222")
        self.driver = webdriver.Chrome(options=chromeOptions, service=ChromeService(ChromeDriverManager().install()))
        
    def __get_product_download_links(self):
        self.driver.get(self.vendor_url)
        
        #andere methode
        selector = self.driver.find_element(By.NAME, "subtype_id")
        options = selector.find_elements(By.XPATH, ".//*")
        
        product_links = []
        
        for d in options:
            pname = d.get_attribute("innerHTML")
            path = d.get_attribute("value")
            if pname or path:
                product = dict(name=d.get_attribute("innerHTML"), link=HOME_URL+d.get_attribute("value"))
                product_links.append(product)
        
        return product_links

    #Extract Download link
    #to_extract format example: MM_openBrWindow('/asp/download_manager/inc_downloading.asp?iFile=29751','29751','width=500,height=300,scrollbars=yes,resizable=yes')"
    def __extract_download_link(self, to_extract: str) -> str:
        split = to_extract.rsplit(',')
        ifile = split[1].replace("'", "")

        downlod_link = DOWNLOAD_BASE_LINK + ifile
        return downlod_link
    
    #convert date to Year-Month-Day
    def __convert_date(self, date_to_convert: str) -> str:
        #5/2018
        splited_date = date_to_convert.split('/')
        
        if len(splited_date) < 2:
            return ''
            
        month = "0" + splited_date[0]
        year = splited_date[1]

        date = year + "-" + month + "-" + "01"

        return date

    def _scrape_product_data(self, p: dict) -> list:
        meta_data = []
        self.driver.get(p["link"])

        try:
            product_header = self.driver.find_element(By.ID, "product-header")
        except selenium.common.exceptions.NoSuchElementException:
            return []
        
        if not product_header:
            return []

        try:
            product_type = product_header.find_element(By.XPATH, '/html/body/main/div[1]/div/div[2]/div/div[1]/h1').get_attribute('innerHTML').lstrip().strip()
        except selenium.common.exceptions.NoSuchElementException:
            return []
     
        #get download links
        downloads = self.driver.find_element(By.ID, "downloads")
        
        if not downloads:
            return []
        
        cards = downloads.find_elements(By.CLASS_NAME, "card")
        
        for c in cards:
            firmware_item = {
                "manufacturer": "Trendnet",
                "product_name": None,
                "product_type": None,
                "version": None,
                "release_date": None,
                "download_link": None,
                "checksum_scraped": None,
                "additional_data": {},
            }

            header = c.find_element(By.CLASS_NAME, "card-header")
            data_type = header.get_attribute("innerHTML")
            
            #if not data_type == "Drivers" and not data_type == "Firmware" and not data_type == "Software":
            if not data_type == "Firmware ":
                continue
            
            row = c.find_element(By.CLASS_NAME, "row")
            
            #finde release date and firmware version
            try:
                tmp = row.find_element(By.TAG_NAME, "p")
            except selenium.common.exceptions.NoSuchElementException:
                continue    
            
            x = (tmp.text).splitlines()
            
            if len(x) < 2:
                continue
            
            splited_version = x[0].rsplit(":")
            splited_release_date = x[1].rsplit(":")

            if len(splited_release_date) < 2 or len(splited_version) < 2:
                continue

            version = splited_version[1]
            release_date = splited_release_date[1]
    
            #find check sum
            try:
                check_sum = ((row.find_element(By.CLASS_NAME, "g-font-size-13").text).rsplit(":"))[1]
            except selenium.common.exceptions.NoSuchElementException:
                check_sum = " "

            download_btn = row.find_element(By.CLASS_NAME, "btn")
            download_link = self.__extract_download_link(download_btn.get_attribute('onclick'))

            firmware_item["product_name"] = p["name"]
            firmware_item["product_type"] = product_type
            firmware_item["version"] = version
            firmware_item["release_date"] = "2023-01-01"
            #firmware_item["release_date"] = self.__convert_date(release_date)
            firmware_item["download_link"] = download_link
            firmware_item["checksum_scraped"] = check_sum

            meta_data.append(firmware_item)

        return meta_data

    def scrape_metadata(self) -> list:
        meta_data = []
        product_download_webpages = self.__get_product_download_links()

        for p in product_download_webpages:
            scraped = self._scrape_product_data(p)
            meta_data = meta_data + scraped

        self.driver.quit()
        return meta_data
                    
def main():
    Scraper = TrendnetScraper()
    meta_data = Scraper.scrape_metadata()

    print(json.dumps(meta_data))
    #Scraper.test_scrape()

if __name__ == "__main__":
    main()