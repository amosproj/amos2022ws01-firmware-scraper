from re import A, X
from unicodedata import category
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import requests

HOME_URL = "https://www.trendnet.com/langge/support/"
MANUFACTURER = "Trendnet"
DRIVER_PATH = "C:\\Users\\Admin\\Desktop\\amos\\chromedriver_win32\\chromedriver.exe"

class Trendnet_Scraper:
    def __init__(self, driver_path: str):
        self.vendor_url = HOME_URL
        self.driver = webdriver.Chrome(driver_path)
        
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
    
    
    def test_scrape(self):
        self.driver.get("https://www.trendnet.com/langge/support/support-detail.asp?prod=130_TV-NVR2432")
        meta_data = []
        
        #get product type
        product_header = self.driver.find_element(By.ID, "product-header")
        product_type = product_header.find_element(By.TAG_NAME, "h1").get_attribute("innerHTML")
        print(product_type)
        
        #get download links
        downloads = self.driver.find_element(By.ID, "downloads")
        cards = downloads.find_elements(By.CLASS_NAME, "card")
        
        for c in cards:
            header = c.find_element(By.CLASS_NAME, "card-header")
            data_type = header.get_attribute("innerHTML")
            
            #if not data_type == "Drivers" and not data_type == "Firmware" and not data_type == "Software":
            if not data_type == "Firmware":
                continue
            
            row = c.find_element(By.CLASS_NAME, "row")
            
            #finde release date and firmware version
            tmp = row.find_element(By.TAG_NAME, "p")
            x = (tmp.text).splitlines()
            version = (x[0].rsplit(":"))[1]
            release_date = (x[1].rsplit(":"))[1]
            print(version)
            print(release_date)
            
            #find check sum
            check_sum = ((row.find_element(By.CLASS_NAME, "g-font-size-13").text).rsplit(":"))[1]
            print(check_sum)

            
        
        
        
    # firmware_item = {
    #                 "manufacturer": "AVM",
    #                 "product_name": None,
    #                 "product_type": None,
    #                 "version": None,
    #                 "release_date": self._convert_date(date),
    #                 "download_link": None,
    #                 "checksum_scraped": None,
    #                 "additional_data": {},
    #             }    
    def get_product_catalog(self):
        product_download_webpages = self.__get_product_download_links()
      
        for p in product_download_webpages:
            self.driver.get(p["link"])
            meta_data = []
            
            #get product type
            product_header = self.driver.find_element(By.ID, "product-header")
            
            if not product_header:
                continue
            
            product_type = product_header.find_element(By.TAG_NAME, "h1").get_attribute("innerHTML")
            print(product_type)
            
            #get download links
            downloads = self.driver.find_element(By.ID, "downloads")
            
            if not downloads:
                continue
            
            cards = downloads.find_elements(By.CLASS_NAME, "card")
            
            for c in cards:
                header = c.find_element(By.CLASS_NAME, "card-header")
                data_type = header.get_attribute("innerHTML")
                
                #if not data_type == "Drivers" and not data_type == "Firmware" and not data_type == "Software":
                if not data_type == "Firmware":
                    continue
                
                row = c.find_element(By.CLASS_NAME, "row")
                
                #finde release date and firmware version
                tmp = row.find_element(By.TAG_NAME, "p")
                x = (tmp.text).splitlines()
                version = (x[0].rsplit(":"))[1]
                release_date = (x[1].rsplit(":"))[1]
                print(version)
                print(release_date)
                
                #find check sum
                check_sum = ((row.find_element(By.CLASS_NAME, "g-font-size-13").text).rsplit(":"))[1]
                print(check_sum)
            
        time.sleep(1)
        
    
        
        
def main():
    Scraper = Trendnet_Scraper(DRIVER_PATH)
    Scraper.get_product_catalog()

if __name__ == "__main__":
    main()