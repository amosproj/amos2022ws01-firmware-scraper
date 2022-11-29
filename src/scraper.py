from unicodedata import category
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import requests

HOME_URL = "https://www.zyxel.com/global/en"
PRODUCT_PATH = "/global/en/products"
MANUFACTURER = "Zyxel Networks"
DOWNLOAD_URL = "https://www.zyxel.com/global/en/support/download"

class Zyxel_Scraper:
    def __init__(self, driver_path: str):
        self.vendor_url = HOME_URL
        self.driver = webdriver.Chrome(driver_path)

    def get_product_category_ulrs(self):
        category_urls = []
        
        menu = self.driver.find_element(By.ID, "block-product-category-mega-menu")
        wrapper = menu.find_elements(By.CLASS_NAME, "product-category-mega-menu-item")
        
        for category in wrapper:
            links = category.find_elements(By.TAG_NAME, "a")    
            cat = category.find_element(By.TAG_NAME, "h3")
            #print(cat.get_attribute("innerHTML"))       
            for link in links:
                if type(link.get_attribute("href")) == str:
                    if PRODUCT_PATH in link.get_attribute("href"):
                        category_urls.append(link.get_attribute("href"))
                        print(cat.get_attribute("innerHTML")+ link.get_attribute("href"))
            
        return category_urls
        
    # firmware_item = {"manufacturer": "Schneider Electric",
    #                      "product_name": title,
    #                      "product_type": product_ranges,
    #                      "version": version,
    #                      "release_date": None,
    #                      "checksum_scraped": None,
    #                      "additional_data": {
    #                          "product_reference": reference,
    #                          "languages": languages
    #                      }
    #                     }
        
    def get_products(self, category_urls: dict):
        products = []
        for category_url in category_urls:
            #print(category_url)
            self.driver.get(category_url)
            
            cat_name = self.driver.find_element(By.CLASS_NAME, "category-name")
            x = cat_name.find_element(By.CLASS_NAME, "field")
            product_type = x.get_attribute("innerHTML")
            print("The category is: " + product_type)
            
            
            products_of_category = self.driver.find_elements(By.CLASS_NAME, "product-item-info")
            
            for product in products_of_category:
                product_name = (product.find_element(By.TAG_NAME, "h5")).get_attribute("innerHTML")
                #print(product_name)
                
                is_in_list = False
                for item in products:
                    if item["product_name"] == product_name:
                        is_in_list = True
                
                if not is_in_list:    
                    firmware_item = {"manufacturer": MANUFACTURER,
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
                #print(firmware_item)
                
            time.sleep(0.3)

        [print(x) for x in products]
        return products
        
    def get_download_links(self, products: list):
        return_list = []
        
        #print(return_list)  

        for product in products:
            self.driver.get(DOWNLOAD_URL)
            element = self.driver.find_element(By.NAME, "model")
            send_button = self.driver.find_element(By.ID, "edit-submit-product-list-by-model")
            pname = product["product_name"]
            element.send_keys(pname)
            send_button.click()
            links = self.driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                if type(link.get_attribute("href")) == str:
                    if ".zip" in link.get_attribute("href"):
                        return_list.append(link.get_attribute("href"))
                        
        for x in return_list:
            res = requests.head(x)
            print(res.headers)
            
        time.sleep(0.4)
        

    def get_product_catalog(self):
        self.driver.get(self.vendor_url)
        category_urls = self.get_product_category_ulrs()
        #print(category_urls)
        products = self.get_products(category_urls)
        self.get_download_links(products)
        #cat = self.driver.find_element(By.ID, "block-product-category-mega-menu")
        #cat_html = cat.get_attribute("innerHTML")
        #print(cat_html)
        
        
        
