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

HOME_URL = "https://www.zyxel.com/global/en"
PRODUCT_PATH = "/global/en/products"
MANUFACTURER = "Zyxel Networks"
DOWNLOAD_URL = "https://www.zyxel.com/global/en/support/download"

class ZyxelScraper:
    def __init__(
            self,
            logger,
            scrape_entry_url: str = DOWNLOAD_URL,
            headless: bool = True,
            max_products: int = float("inf"),
        ):
        self.vendor_url = HOME_URL
        chromeOptions = webdriver.ChromeOptions() 
        webdriver.ChromeOptions()
        self.name = "Zyxel"
        chromeOptions.add_argument("--disable-dev-shm-using") 
        chromeOptions.add_argument("--remote-debugging-port=9222")
        self.driver = webdriver.Chrome(options=chromeOptions, service=ChromeService(ChromeDriverManager().install()))

    #get links to each category where products can be found 
    def __get_product_category_ulrs(self) -> list:
        category_urls = []
        
        menu = self.driver.find_element(By.ID, "block-product-category-mega-menu")
        wrapper = menu.find_elements(By.CLASS_NAME, "product-category-mega-menu-item")
        
        for category in wrapper:
            links = category.find_elements(By.TAG_NAME, "a")    
            cat = category.find_element(By.TAG_NAME, "h3")

            for link in links:
                if type(link.get_attribute("href")) == str:
                    if PRODUCT_PATH in link.get_attribute("href"):
                        category_urls.append(link.get_attribute("href"))
            
        return category_urls
        
    def __get_products(self, category_urls: list):
        products = []

        #get all products of each category
        for category_url in category_urls:
            self.driver.get(category_url)
            
            #get name of the category
            cat_name = self.driver.find_element(By.CLASS_NAME, "category-name")
            product_type = (cat_name.find_element(By.CLASS_NAME, "field")).get_attribute("innerHTML")
            
            #get element of table which contains all products of this category
            products_of_category = self.driver.find_elements(By.CLASS_NAME, "product-item-info")
            
            #loop through each product in category
            for product in products_of_category:
                #get product name
                product_name = (product.find_element(By.TAG_NAME, "h5")).get_attribute("innerHTML")

                #dont insert again if product is already in list
                is_in_list = False
                for item in products:
                    if item["product_name"] == product_name:
                        is_in_list = True
                
                if not is_in_list:    
                    firmware_item = {
                            "manufacturer": MANUFACTURER,
                            "product_name": product_name,
                            "product_type": product_type,
                            "version": None,
                            "release_date": None,
                            "checksum_scraped": None,
                            "additional_data": {
                                "product_reference": None,
                                "languages": None
                            }
                        }
                    products.append(firmware_item)
                
        #get products of series
        ser = []
        for p in products:
            if "Series" in p["product_name"]:
                self.driver.get("https://www.zyxel.com/global/en/support/download")
                element = self.driver.find_element(By.NAME, "model")
                pname = p["product_name"].replace("Series", " ")
                element.send_keys(pname)
                element.send_keys(" ")
                time.sleep(1)
                suggestions = self.driver.find_elements(By.CLASS_NAME, "ui-menu-item")

                for s in suggestions:
                    new_name = s.find_element(By.CLASS_NAME, "autocomplete-suggestion-label").get_attribute("innerHTML")
                    firmware_item = {"manufacturer": MANUFACTURER,
                            "product_name": new_name,
                            "product_type": p["product_type"],
                            "version": None,
                            "release_date": None,
                            "checksum_scraped": None,
                            "additional_data": {
                                "product_reference": None,
                                "languages": None
                            }
                            }
                    ser.append(firmware_item)

        products = [i for i in products if not ("Series" in i['product_name'])]
        
        products = products + ser        
        return products

    #convert date to Year-Month-Day
    def __convert_date(self, date_to_convert:str) -> str:
        date_to_convert = date_to_convert.replace(',', '')
        split_date = date_to_convert.split()

        if 'Januar' in split_date[0]:
            month = '01'
        elif 'Februar' in split_date[0]:
            month = '02'
        elif 'März' in split_date[0]:
            month = '03'
        elif 'April' in split_date[0]:
            month = '04'
        elif 'Mai' in split_date[0]:
            month = '05'
        elif 'Juni' in split_date[0]:
            month = '06'
        elif 'Juli' in split_date[0]:
            month = '07'
        elif 'August' in split_date[0]:
            month = '08'
        elif 'September' in split_date[0]:
            month = '09'
        elif 'Oktober' in split_date[0]:
            month = '10'
        elif 'November' in split_date[0]:
            month = '11'
        elif 'Dezember' in split_date[0]:
            month = '12'
        else:
            month = '12'
            
        final_date = split_date[2] + '-' + month + '-' + split_date[1]

        return final_date
        
    def __get_download_links(self, products: list):
        meta_data = []

        for p in products:
            #type in product name in searchbar
            self.driver.get("https://www.zyxel.com/global/en/support/download")
            element = self.driver.find_element(By.NAME, "model")
            send_button = self.driver.find_element(By.ID, "edit-submit-product-list-by-model")
            pname = p["product_name"]
            ptype = p["product_type"]
            element.send_keys(pname)
            send_button.click()

            table_elements = self.driver.find_elements(By.TAG_NAME, "tr")

            #scrape metadata from table
            for element in table_elements:
                val = element.find_elements(By.TAG_NAME, "td")

                #first read view-nothing-2-table-column to check if it is firmware or driver... if not skip
                if len(val) == 0:
                    continue
                if not "Driver" in val[1].text and not "Firmware" in val[1].text:
                        continue

                firmware_item = {
                        "manufacturer": "Zyxel",
                        "product_name": pname,
                        "product_type": ptype,
                        "version": None,
                        "release_date": None,
                        "download_link": None,
                        "checksum_scraped": None,
                        "additional_data": {},
                    }

                #fill meta data to product
                for con in val:
                    header = con.get_attribute("headers")

                    if "view-model-name-table-column" in header:
                        pass
                    elif "view-nothing-2-table-column" in header:
                        pass
                    elif "view-field-version-table-column" in header: #version
                        firmware_item["version"] = con.text
                    elif "view-nothing-1-table-column" in header: #download link
                        tmp = con.find_element(By.CLASS_NAME, "modal-footer")
                        firmware_item["download_link"] = tmp.find_element(By.TAG_NAME,"a").get_attribute("href")
                    elif "view-nothing-table-column" in header: #checksum
                        try:
                            tmp = con.find_element(By.CLASS_NAME, "modal-body").find_elements(By.TAG_NAME, "p")
                            firmware_item["checksum_scraped"] = tmp[1].get_attribute("innerHTML")
                        except selenium.common.exceptions.NoSuchElementException:
                            continue
                    elif "view-field-release-date-table-column" in header: #release date
                        firmware_item["release_date"] = self.__convert_date(con.text)

                meta_data.append(firmware_item)

        return meta_data
    
    def scrape_metadata(self) -> list:
        self.driver.get(self.vendor_url)
        category_urls = self.__get_product_category_ulrs()
        products = self.__get_products(category_urls)
        meta_data = self.__get_download_links(products)

        self.driver.quit()   
        return meta_data

def main():
    Scraper = ZyxelScraper()
    meta_data = Scraper.scrape_metadata()
    print(json.dumps(meta_data))

if __name__ == "__main__":
    main()