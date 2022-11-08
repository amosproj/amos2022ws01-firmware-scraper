# # Import packages

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

from selenium.webdriver.chrome.options import Options

import time
import pandas as pd
from tqdm import tqdm

# # STATICS


VENDOR_URL = 'https://www.synology.com/en-global/support/download'
PRODUCT_TYPE_SELECTOR = 'div.margin_bottom20 > select:nth-child(1)'
PRODUCT_SELECTOR = '//*[@id="heading_bg"]/div/div/div[2]/select'
NEWEST_OS_SELECTOR = '//*[@id="results"]/div[3]/div[2]/div[1]/div/div[1]/div[1]/div/div/div[1]'
DOWNLOAD_PATH = '/Users/kiril/Downloads/selenium_downloads'

# Selenium Webdriver Options, Download Path, Headless, Screensize, Webbrowser Version
options = Options()
options.headless = True

options.add_experimental_option("prefs", {
    "download.default_directory": rf"{DOWNLOAD_PATH}"
})

# # Initialize Chrome and open Vendor Website


class Synology_scraper:

    def __init__(
        self,
        url: str,
        headless: bool,
        options: Options,
    ):  
        print(f"headless: {options.headless}")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.url = url
        print('Initialized successfully')


    def open_website(self):
        try:
            self.driver.get(self.url)
            print('Opened Website')
        except:
            print('nix')
            pass

    def create_product_catalog(self):
        """_summary_

        Returns:
            dict: _description_
        """
        sel = Select(self.driver.find_element(By.CSS_SELECTOR, value=f"{PRODUCT_TYPE_SELECTOR}"))
        
        # set keys as product_lines
        product_catalog = dict.fromkeys([elem.text for elem in sel.options[1:]], None)
        # set values from products of product line
        for product in product_catalog.keys():
            sel.select_by_visible_text(product)
            selector_products = Select(self.driver.find_element(By.XPATH, value=f"{PRODUCT_SELECTOR}"))
            product_catalog[product] = [elem.text for elem in selector_products.options[1:]]
        print('created product_catalog')
        self.product_catalog = product_catalog

    def download_product(self) -> bool:
        """_summary_

        Returns:
            bool: _description_
        """

    def choose_product_line(self, product_line=str) -> None:
        sel = Select(self.driver.find_element(By.CSS_SELECTOR, value='div.margin_bottom20 > select:nth-child(1)'))
        
        sel.select_by_visible_text(product_line)
        selector_products = Select(self.driver.find_element(By.XPATH, value='//*[@id="heading_bg"]/div/div/div[2]/select'))
        #return [elem.text for elem in selector_products.options[1:]]

    def choose_product(self, product=str) -> (str,str,str):
        self.driver.implicitly_wait(10)
        time.sleep(1)
        selector_products = Select(self.driver.find_element(By.XPATH, value=f'{PRODUCT_SELECTOR}'))
        selector_products.select_by_visible_text(product)
        # newest OS Version
        self.driver.implicitly_wait(1)
        selector_OS = self.driver.find_element(By.XPATH, value=f'{NEWEST_OS_SELECTOR}')

        # return MD5 checksum and DSM newest OS Version and current URL
        return self.get_MD5_checksum(), selector_OS.text, self.driver.current_url
    
    def download_product(self, product=str) -> bool:
        """
        """
        try:
            el = self.driver.find_element(By.XPATH, value='//*[@id="results"]/div[3]/div[2]/div[1]/div/div[1]/div[1]/div/div/div[3]/div/div/div/div[1]/a')
            el.click()
            return True
        except:
            False
        
    def get_MD5_checksum(self) -> str:
        el = self.driver.find_element(By.XPATH, value='//*[@id="results"]/div[3]/div[2]/div[1]/div/div[1]/div[1]/div/div/div[3]/div/div/div/div[2]/div[2]/div/a')
        return el.get_attribute('title').replace('\n(Copy to Clipboard)','')




def main():

    Syn = Synology_scraper(VENDOR_URL, headless=False, options=options)
    Syn.open_website()
    Syn.create_product_catalog()

    #Test
    Syn.choose_product_line('NAS')
    Syn.choose_product('RS408')

    # Fill up dataframe with results
    result_df = pd.DataFrame(columns=[
                            'vendor', 'product_line', 'product', 'MD5', 'DSM', 'url', 'downloaded', 'exception_e'])

    for product_line in Syn.product_catalog.keys():
        Syn.choose_product_line(product_line)

        for i, product in tqdm(enumerate(Syn.product_catalog[product_line])):
            print(product_line, product)
            appendix = []
            appendix.append('Synology')
            appendix.append(product_line)
            appendix.append(str(product))
            try:
                md5, dsm, url = Syn.choose_product(f'{product}')
                appendix.append(md5)
                appendix.append(dsm)
                appendix.append(url)
                appendix.append('NotImplemented')
                appendix.append('')
            except Exception as e:
                appendix.append("")
                appendix.append("")
                appendix.append("")
                appendix.append("NotImplemented")
                appendix.append(str(e))
            result_df = result_df.append(pd.DataFrame([appendix], columns=result_df.columns), ignore_index=True)

    # show df
    result_df

    # save df
    result_df.to_csv(f'{DOWNLOAD_PATH}+everyone.csv')

if __name__ == "__main__":
    main()
    # print END
    print('END')