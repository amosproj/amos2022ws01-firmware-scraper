# # Import packages

import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager

# # STATICS
VENDOR_URL = 'https://www.synology.com/en-global/support/download/'
PRODUCT_TYPE_SELECTOR = 'div.margin_bottom20 > select:nth-child(1)'
PRODUCT_SELECTOR = '//*[@id="heading_bg"]/div/div/div[2]/select'
NEWEST_OS_SELECTOR = '//*[@id="results"]/div[3]/div[2]/div[1]/div/div[1]/div[1]/div/div/div[1]'
DOWNLOAD_SELECTOR = '//*[@id="results"]/div[3]/div[2]/div[1]/div/div[1]/div[1]/div/div/div[3]/div/div/div/div[1]/a'
DOWNLOAD_PATH = 'data/'

# Selenium Webdriver Options, Download Path, Headless, Screensize, Webbrowser Version
options = Options()
options.headless = False

options.add_experimental_option("prefs", {
    "download.default_directory": rf"{DOWNLOAD_PATH}"
})

# # Initialize Chrome and open Vendor Website


class Synology_scraper:

    def __init__(
        self,
        url: str = VENDOR_URL,
        headless: bool = False,
        options: Options = options,
        max_products: int = float('inf')
    ):
        self.headless = headless
        self.url = url
        self.max_products = max_products
        self.driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()), options=options)
        self.driver.implicitly_wait(0.5)  # has to be set only once
        print('Initialized successfully')

    def _create_product_catalog(self) -> dict:
        """clicks once through all product lines and products and saves them in a dict

        Returns:
            dict: product catalog
        """

        sel = Select(self.driver.find_element(
            By.CSS_SELECTOR, value=f"{PRODUCT_TYPE_SELECTOR}"))

        # set keys as product_lines
        product_catalog = dict.fromkeys(
            [elem.text for elem in sel.options[1:]], None)
        # set values from products of product line
        for product in product_catalog.keys():
            sel.select_by_visible_text(product)
            selector_products = Select(self.driver.find_element(
                By.XPATH, value=f"{PRODUCT_SELECTOR}"))
            product_catalog[product] = [
                elem.text for elem in selector_products.options[1:]]
        print('created product_catalog')
        return product_catalog

    def _choose_product_line(self, product_line: str) -> None:
        """selects product line on vendor website

        Args:
            product_line (str): product line to select
        """
        sel = Select(self.driver.find_element(By.CSS_SELECTOR,
                     value='div.margin_bottom20 > select:nth-child(1)'))

        sel.select_by_visible_text(product_line)
        selector_products = Select(self.driver.find_element(
            By.XPATH, value='//*[@id="heading_bg"]/div/div/div[2]/select'))
        # return [elem.text for elem in selector_products.options[1:]]

    def _choose_product(self, product: str) -> (str, str, str):
        """selects product on vendor website after selecting product line

        Args:
            product (str): product to select

        Returns:
            list[str]: MD5 checksum, list of available OS, drivers current url
        """
        self.driver.implicitly_wait(10)
        time.sleep(1)
        selector_products = Select(self.driver.find_element(
            By.XPATH, value=f'{PRODUCT_SELECTOR}'))
        selector_products.select_by_visible_text(product)
        # newest OS Version
        self.driver.implicitly_wait(1)
        selector_OS = self.driver.find_element(
            By.XPATH, value=f'{NEWEST_OS_SELECTOR}')

        # return MD5 checksum and DSM newest OS Version and current URL
        return self._get_MD5_checksum(), selector_OS.text, self.driver.current_url

    def download_product(self, product: str) -> bool:
        """
        """
        try:
            el = self.driver.find_element(
                By.XPATH, value=DOWNLOAD_SELECTOR)
            el.click()
            return True
        except Exception as e:
            print(e)
            return False

    def find_download_link(self, product_line: str, product: str) -> str:
        self._choose_product_line(product_line)
        self._choose_product(product)
        self.download_product(product)
        return self._get_MD5_checksum()

    def _get_MD5_checksum(self) -> str:
        el = self.driver.find_element(
            By.XPATH, value='//*[@id="results"]/div[3]/div[2]/div[1]/div/div[1]/div[1]/div/div/div[3]/div/div/div/div[2]/div[2]/div/a')
        return el.get_attribute('title').replace('\n(Copy to Clipboard)', '')

    def scrape_metadata(self) -> list[dict]:
        """function that gets executed from Core.py to scrape metadata 
            and search for firmwares

        Returns:
            list[dict]: list of dicts with metadata
        """
        # open website
        self.driver.get(self.url)
        # create product catalog
        product_catalog = self._create_product_catalog()
        # create list of dicts with metadata
        metadata = []
        for product_line in product_catalog.keys():
            self._choose_product_line(product_line)
            for product in tqdm(product_catalog[product_line]):
                self._choose_product(product)
                metadata.append({'manufacturer': 'Synology',
                                 'product_type': product_line,
                                 'product_name': product,
                                 'url': self.driver.current_url,
                                 'checksum_scraped': self._get_MD5_checksum(),
                                 'download_link': 'not implemented'
                                 })
                if len(metadata) > self.max_products:
                    break
        self.driver.quit()
        return metadata


def main():

    Syn = Synology_scraper()
    Syn.open_website()
    Syn._create_product_catalog()

    # Fill up dataframe with results
    result_df = pd.DataFrame(columns=[
        'vendor', 'product_line', 'product', 'MD5', 'DSM', 'url', 'downloaded', 'exception_e'])

    for product_line in Syn.product_catalog.keys():
        Syn._choose_product_line(product_line)

        for i, product in tqdm(enumerate(Syn.product_catalog[product_line])):
            print(product_line, product)
            appendix = []
            appendix.append('Synology')
            appendix.append(product_line)
            appendix.append(str(product))
            try:
                md5, dsm, url = Syn._choose_product(f'{product}')
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
            result_df = result_df.append(pd.DataFrame(
                [appendix], columns=result_df.columns), ignore_index=True)

    # show df
    result_df

    # save df
    result_df.to_csv(f'{DOWNLOAD_PATH}everyone.csv')


if __name__ == "__main__":
    main()
    # print END
    print('END')
