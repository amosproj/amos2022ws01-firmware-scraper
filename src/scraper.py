from selenium import webdriver
from selenium.webdriver.common.by import By

class Zyxel_Scraper:
    def __init__(self, vendor_url: str, driver_path: str):
        self.vendor_url = vendor_url
        self.driver = webdriver.Chrome(driver_path)

    def get_download_links(self):
        return_list = []
        self.driver.get(self.vendor_url)
        links = self.driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            if type(link.get_attribute("href")) == str:
                if ".zip" in link.get_attribute("href"):
                    return_list.append(link.get_attribute("href"))  
        return return_list
