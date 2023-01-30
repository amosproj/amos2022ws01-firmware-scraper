import time

from selenium.webdriver.common.by import By

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException
from src.Vendors.scraper import Scraper
from src.logger import *

HOME_URL = "https://www.zyxel.com/global/en"
PRODUCT_PATH = "/global/en/products"
MANUFACTURER = "Zyxel Networks"
DOWNLOAD_URL = "https://www.zyxel.com/global/en/support/download"

ignored_exceptions = (NoSuchElementException,
                      StaleElementReferenceException,
                      ElementNotInteractableException,
                      ElementClickInterceptedException)


class ZyxelScraper(Scraper):
    def __init__(
        self,
        driver,
        scrape_entry_url: str = DOWNLOAD_URL,
        headless: bool = True,
        max_products: int = float("inf"),
    ):
        self.scrape_entry_url = scrape_entry_url
        self.name = "Zyxel"
        self.__scrape_cnt = 0
        self.max_products = max_products
        self.headless = headless
        self.logger = get_logger()
        self.driver = driver

    """Get Links to each category where products can be found"""

    def __get_product_category_ulrs(self) -> list:
        category_urls = []

        self.logger.info('Start Scrape -> Category URLs')

        try:
            menu = self.driver.find_element(
                By.ID, "block-product-category-mega-menu")
            wrapper = menu.find_elements(
                By.CLASS_NAME, "product-category-mega-menu-item")

            for category in wrapper:
                links = category.find_elements(By.TAG_NAME, "a")

                for link in links:
                    if type(link.get_attribute("href")) == str:
                        if PRODUCT_PATH in link.get_attribute("href"):
                            category_urls.append(link.get_attribute("href"))
        except Exception as e:
            self.logger.error(
                'Abort Scraper. Failed to Scrape Category Urls -> ' + str(e))
            return []

        self.logger.important('Successfully Scraped -> Category URLs -> '
                              + str(len(category_urls))
                              + " Categorys found")
        return category_urls

    def __get_products(self, category_urls: list):
        products = []

        self.logger.info('Start Scrape -> Product URLs')

        # get all products of each category
        for category_url in category_urls:
            try:
                self.driver.get(category_url)

                # get name of the category
                cat_name = self.driver.find_element(
                    By.CLASS_NAME, "category-name")
                product_type = (cat_name.find_element(
                    By.CLASS_NAME, "field")).get_attribute("innerHTML")

                # get element of table which contains all products of this category
                products_of_category = self.driver.find_elements(
                    By.CLASS_NAME, "product-item-info")

                self.logger.info('Start searching for Products -> (Category)'
                                 + product_type)
            except Exception as e:
                self.logger\
                    .error("Failed to get category url. Skip Category -> " + str(e))
                continue

            # loop through each product in category
            for product in products_of_category:

                try:
                    # get product name
                    product_name = (product.find_element(
                        By.TAG_NAME, "h5")).get_attribute("innerHTML")
                except Exception as e:
                    self.logger\
                        .error("Failed to Get Product. Skip product -> (Category)"
                               + product_type
                               + " -> "
                               + str(e))
                    continue

                # dont insert again if product is already in list
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

        self.logger.info('Scrape individual Product of Product Series.')
        # get products of series
        ser = []
        for p in products:
            if "Series" in p["product_name"]:
                try:
                    self.driver.get(
                        "https://www.zyxel.com/global/en/support/download")
                    element = self.driver.find_element(By.NAME, "model")
                    pname = p["product_name"].replace("Series", " ")
                    element.send_keys(pname)
                    element.send_keys(" ")
                    time.sleep(1)
                    suggestions = self.driver.find_elements(
                        By.CLASS_NAME, "ui-menu-item")
                except Exception as e:
                    self.logger\
                        .error("Failed to open suggestion window -> (Product)"
                               + p["product_name"]
                               + " -> "
                               + str(e))
                    continue

                for s in suggestions:
                    try:
                        new_name = s.find_element(
                            By.CLASS_NAME, "autocomplete-suggestion-label").get_attribute("innerHTML")
                    except Exception as e:
                        self.logger\
                            .error("Failed to get autocomplete suggestion, skip -> (Product in Series)"
                                   + p["product_name"]
                                   + " ->"
                                   + str(e))
                        continue

                    firmware_item = {
                        "manufacturer": MANUFACTURER,
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

        self.logger.important('Scraped Category Product URLs. Products Found -> '
                              + str(len(products)))
        return products

    """convert date to Year-Month-Day"""

    def __convert_date(self, date_to_convert: str) -> str:
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

        self.logger.info('Start Scraping Firmware')

        for p in products:
            # type in product name in searchbar
            try:
                self.driver.get(
                    "https://www.zyxel.com/global/en/support/download")
                element = self.driver.find_element(By.NAME, "model")
                send_button = self.driver.find_element(
                    By.ID, "edit-submit-product-list-by-model")
                pname = p["product_name"]
                ptype = p["product_type"]
                element.send_keys(pname)
                send_button.click()

                table_elements = self.driver.find_elements(By.TAG_NAME, "tr")
            except Exception as e:
                self.logger\
                    .error("Failed to Scrape Firmware. Skip -> (Product)"
                           + p["product_name"]
                           + " -> "
                           + str(e))
                continue

            # scrape metadata from table
            for element in table_elements:
                try:
                    val = element.find_elements(By.TAG_NAME, "td")
                except Exception as e:
                    self.logger.error(
                        "Failed to Scrape Download Table Row. Skip Row -> (Product)"
                        + pname
                        + " -> "
                        + str(e))
                    continue

                # first read view-nothing-2-table-column to check if it is firmware or driver... if not skip
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

                # fill meta data to product
                for con in val:
                    try:
                        header = con.get_attribute("headers")

                        if "view-model-name-table-column" in header:
                            pass
                        elif "view-nothing-2-table-column" in header:
                            pass
                        elif "view-field-version-table-column" in header:  # version
                            firmware_item["version"] = con.text
                        elif "view-nothing-1-table-column" in header:  # download link
                            tmp = con.find_element(
                                By.CLASS_NAME, "modal-footer")
                            firmware_item["download_link"] = tmp.find_element(
                                By.TAG_NAME, "a").get_attribute("href")
                        elif "view-nothing-table-column" in header:  # checksum
                            tmp = con.find_element(
                                By.CLASS_NAME, "modal-body").find_elements(By.TAG_NAME, "p")
                            firmware_item["checksum_scraped"] = tmp[1].get_attribute(
                                "innerHTML")
                        elif "view-field-release-date-table-column" in header:  # release date
                            firmware_item["release_date"] = self.__convert_date(
                                con.text)
                    except Exception as e:
                        self.logger.error(
                            "Failed to Scrape Firmware. Skip Firmware -> (Product)"
                            + pname
                            + " -> "
                            + str(e))
                        continue

                meta_data.append(firmware_item)

        self.logger.important('Scraped Products -> (Total)'
                              + str(len(products))
                              + ' -> Found Firmware -> (Total)'
                              + str(len(meta_data)))
        return meta_data

    def scrape_metadata(self) -> list:
        self.logger.important('Start Scrape Vendor -> Zyxel')
        self.logger.important(
            'Scrape in Headless Mode Set -> ' + str(self.headless))
        self.logger.important('Max Products Set-> ' + str(self.max_products))

        try:
            self.driver.get(self.scrape_entry_url)
            self.logger.important("Successfully accessed entry point URL -> "
                                  + self.scrape_entry_url)
        except Exception as e:
            self.logger\
                .error("Abort scraping. Could not access entry point URL -> "
                       + self.scrape_entry_url
                       + " -> "
                       + str(e))
            self.driver.quit()
            return []

        category_urls = self.__get_product_category_ulrs()
        products = self.__get_products(category_urls)

        if len(products) > self.max_products:
            products = products[0:self.max_products]

        meta_data = self.__get_download_links(products)

        self.driver.quit()
        self.logger.info('Meta Data found -> ' + str(len(meta_data)))
        self.logger.info('Finished Scraping Zyxel.')
        return meta_data


if __name__ == "__main__":
    Scraper = ZyxelScraper(max_products=15, logger=None)
    meta_data = Scraper.scrape_metadata()
