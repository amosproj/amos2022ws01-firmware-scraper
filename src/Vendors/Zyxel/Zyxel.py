import time

from selenium.webdriver.common.by import By

from src.Vendors.scraper import Scraper
from src.logger import *

HOME_URL = "https://www.zyxel.com/global/en"
PRODUCT_PATH = "/global/en/products"
MANUFACTURER = "Zyxel Networks"
DOWNLOAD_URL = "https://www.zyxel.com/global/en/support/download"

ignored_exceptions = (Exception)


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
        self.max_products = max_products
        self.headless = headless
        self.logger = get_logger()
        self.driver = driver

    """Get Links to each category where products can be found"""

    def __get_product_category_ulrs(self) -> list:
        category_urls = []

        self.logger.debug('Start Scrape Category URLs')

        try:
            menu = self.driver.find_element(
                By.ID,
                "block-product-category-mega-menu"
            )

            wrapper = menu.find_elements(
                By.CLASS_NAME,
                "product-category-mega-menu-item"
            )

            for category in wrapper:
                links = category.find_elements(By.TAG_NAME, "a")
                for link in links:
                    if type(link.get_attribute("href")) == str:
                        if PRODUCT_PATH in link.get_attribute("href"):
                            category_urls.append(link.get_attribute("href"))
        except Exception:
            self.logger.error(
                'Abort Scraper. Failed to Scrape Category Urls'
            )
            return []

        self.logger.debug(
            'Successfully Scraped -> Category URLs -> '
            + str(len(category_urls))
            + " Categorys found"
        )
        return category_urls

    def __load_more_products(self):
        try:
            while True:
                more_btn = self.driver\
                    .find_element(By.XPATH, '//li[@class="pager__item"]')\
                    .find_element(By.CLASS_NAME, 'button')

                more_btn.click()
                time.sleep(2)
        except Exception:
            time.sleep(2)
            pass

    def __get_products(self, category_urls: list):
        products = []

        self.logger.debug('Start Scrape -> Product URLs')

        # get all products of each category
        for category_url in category_urls:
            try:
                self.driver.get(category_url)
                self.__load_more_products()

                # get name of the category
                cat_name = self.driver.find_element(
                    By.CLASS_NAME,
                    "category-name"
                )

                product_type = (cat_name.find_element(
                    By.CLASS_NAME,
                    "field")
                ).get_attribute("innerHTML")

                # get element of table which contains  products of category
                products_of_category = self.driver.find_elements(
                    By.CLASS_NAME,
                    "product-item-info"
                )

                self.logger.debug(
                    'Start searching for Products in -> (Category)'
                    + product_type
                )
            except Exception:
                self.logger.warning(
                    "Failed to get category url. Skip Category"
                )
                continue

            # loop through each product in category
            for product in products_of_category:
                try:
                    # get product name
                    product_name = (product.find_element(By.TAG_NAME, "h5"))\
                        .get_attribute("innerHTML")
                except Exception:
                    self.logger.warning(
                        "Failed to Get Product. Skip product in -> (Category)"
                        + product_type
                    )
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

        self.logger.debug('Scrape individual Product of Product Series.')

        # get products of series
        ser = []
        for p in products:
            if "Series" in p["product_name"]:
                try:
                    self.driver.get(
                        "https://www.zyxel.com/global/en/support/download"
                    )

                    element = self.driver.find_element(By.NAME, "model")
                    pname = p["product_name"].replace("Series", " ")
                    element.send_keys(pname)
                    element.send_keys(" ")
                    time.sleep(1)

                    suggestions = self.driver.find_elements(
                        By.CLASS_NAME,
                        "ui-menu-item"
                    )
                except Exception:
                    self.logger.warning(
                        "Failed to open suggestion window -> (Product)"
                        + p["product_name"]
                    )
                    continue

                for s in suggestions:
                    try:
                        new_name = s.find_element(
                            By.CLASS_NAME, "autocomplete-suggestion-label"
                        ).get_attribute("innerHTML")
                    except Exception:
                        self.logger.warning(
                            "Failed to get autocomplete suggestion, skip -> "
                            + p["product_name"]
                        )
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

        self.logger.debug(
            'Scraped Category Product URLs. Products Found -> '
            + str(len(products))
        )

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

        self.logger.debug('Start Scraping Firmware')

        for p in products:
            # type in product name in searchbar
            try:
                self.driver.get(
                    "https://www.zyxel.com/global/en/support/download"
                )

                element = self.driver.find_element(By.NAME, "model")
                send_button = self.driver.find_element(
                    By.ID,
                    "edit-submit-product-list-by-model"
                )

                pname = p["product_name"]
                ptype = p["product_type"]
                element.send_keys(pname)
                send_button.click()

                table_elements = self.driver.find_elements(By.TAG_NAME, "tr")
            except Exception:
                self.logger.debug(
                    "Failed to Scrape Firmware. Skip -> (Product)"
                    + p["product_name"]
                )
                continue

            time.sleep(1)

            # scrape metadata from table
            for element in table_elements:
                time.sleep(1)
                try:
                    val = element.find_elements(By.TAG_NAME, "td")
                except Exception:
                    self.logger.debug(
                        "Failed to Scrape Download Table Row. Skip Row -> "
                        + pname
                    )
                    continue

                if len(val) == 0:
                    continue

                if "Driver" and "Firmware" not in val[1].text:
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
                        elif "view-field-version-table-column" in header:
                            firmware_item["version"] = con.text
                        elif "view-nothing-1-table-column" in header:
                            tmp = con.find_element(
                                By.CLASS_NAME,
                                "modal-footer"
                            )

                            firmware_item["download_link"] = tmp.find_element(
                                By.TAG_NAME,
                                "a"
                            ).get_attribute("href")
                        elif "view-nothing-table-column" in header:  # checksum
                            try:
                                tmp = con.find_element(
                                    By.CLASS_NAME,
                                    "modal-body"
                                ).find_elements(By.TAG_NAME, "p")

                                firmware_item["checksum_scraped"] = tmp[1]\
                                    .get_attribute("innerHTML")
                            except Exception:
                                firmware_item["checksum_scraped"] = None
                                self.logger.debug('Could not Find Checksum')
                        elif "view-field-release-date-table-column" in header:
                            firmware_item["release_date"] = self\
                                .__convert_date(con.text)
                    except Exception:
                        self.logger.debug(
                            "Failed to Scrape Firmware. Skip Firmware -> "
                            + pname
                        )
                        continue

                self.logger.info(
                    firmware_scraping_success(
                        f"{pname} {firmware_item['download_link']}"
                    )
                )
                meta_data.append(firmware_item)

        self.logger.debug('Scraped Products -> (Total)'
                          + str(len(products))
                          + ' -> Found Firmware -> (Total)'
                          + str(len(meta_data)))
        return meta_data

    def scrape_metadata(self) -> list:
        self.logger.important(start_scraping())

        self.logger.debug(
            'Scrape in Headless Mode Set -> '
            + str(self.headless)
        )

        self.logger.debug(
            'Max Products Set-> '
            + str(self.max_products)
        )

        try:
            self.driver.get(self.scrape_entry_url)
            self.logger.important(
                entry_point_url_success(self.scrape_entry_url)
            )
        except Exception:
            self.logger.error(entry_point_url_failure(self.scrape_entry_url))
            self.driver.quit()
            return []

        category_urls = self.__get_product_category_ulrs()
        products = self.__get_products(category_urls)

        if len(products) > self.max_products:
            products = products[0:self.max_products]

        meta_data = self.__get_download_links(products)

        self.driver.quit()
        self.logger.debug('Meta Data found -> ' + str(len(meta_data)))
        self.logger.important(finish_scraping())
        return meta_data


if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    options = Options()
    # options.add_argument("--headless")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    Scraper = ZyxelScraper(driver=driver, headless=False)
    meta_data = Scraper.scrape_metadata()
