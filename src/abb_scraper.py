from re import A
from unicodedata import category
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import requests

HOME_URL = "https://library.abb.com/r?dkg=dkg_software&q=firmware"
MANUFACTURER = "ABB"
DRIVER_PATH = "C:\\Users\\Admin\\Desktop\\amos\\chromedriver_win32\\chromedriver.exe"

class ABB_Scraper:
    def __init__(self, driver_path: str):
        self.vendor_url = HOME_URL
        self.driver = webdriver.Chrome(driver_path)
        
    def get_product_catalog(self):
        self.driver.get(self.vendor_url)
        accept_btn = self.driver.find_elements(By.XPATH, '//*[@data-locator="privacy-notice-confirmation-accept-btn"]')
        
        if accept_btn:
            accept_btn[0].click()
        
        app = self.driver.find_element(By.ID, 'app')
        print(app.get_attribute('innerHTML'))
        
        rows = app.find_elements(By.XPATH, '//*[@data-locator="search-result-row"]')
        #rows = self.driver.find_elements(By.CLASS_NAME, "sc-bPjxgn rUgvm")
        
        print(rows)
        for row in rows:
            print(row.get_attribute("innerHTML"))
            
        time.sleep(5)
        
        
def main():
    #Scraper = Zyxel_Scraper(DRIVER_PATH)
    #Scraper.get_product_catalog()
    
    Scraper = ABB_Scraper(DRIVER_PATH)
    Scraper.get_product_catalog()

if __name__ == "__main__":
    main()