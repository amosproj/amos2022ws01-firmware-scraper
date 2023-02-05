import time
import json
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from src.Vendors.scraper import Scraper
from src.logger import *

HOME_URL = "https://www.qnap.com/en/download?model=qutscloud&category=firmware"
MANUFACTURER = "Qnap"


class QnapScraper(Scraper):
    def __init__(
        self,
        driver,
        scrape_entry_url: str = HOME_URL,
        headless: bool = True,
        max_products: int = float("inf")
    ):
        self.scrape_entry_url = scrape_entry_url
        self.logger = get_logger()
        self.max_products = max_products
        self.headless = headless
        self.name = MANUFACTURER
        self.__scrape_cnt = 0
        self.driver = driver

    """BUG: CANT CLICK ON REACT BUTTON """

    def __select_firmware(self) -> bool:
        try:
            sel_download_sec = self.driver.find_element(
                By.CLASS_NAME,
                'download-type'
            )

            sel_btns = sel_download_sec.find_elements(
                By.TAG_NAME,
                'button'
            )

            for i in range(0, len(sel_btns)):
                if 'Operating System' in sel_btns[i]\
                        .get_attribute('innerHTML'):
                    return True
        except Exception:
            self.logger.debug(
                'Could not find Firmware Button Selector'
            )
            return False

        return False

    def __get_type_selector(self):
        try:
            sel_selector = self.driver.find_element(By.CLASS_NAME, 'selector')
            sel_choices = sel_selector.find_elements(
                By.CLASS_NAME,
                'choice-set'
            )

            time.sleep(2)

            sel_type_selector = sel_choices[0].find_element(
                By.TAG_NAME,
                'select'
            )

            sel_type_options = sel_type_selector.find_elements(
                By.XPATH,
                './/*'
            )

            time.sleep(2)

            type_selector = Select(sel_type_selector)
        except Exception:
            self.logger.warning('Could not Select Product Type')
            return ([], [])

        return (type_selector, sel_type_options)

    def __get_model_selector(self):
        try:
            sel_selector = self.driver.find_element(By.CLASS_NAME, 'selector')
            sel_choices = sel_selector.find_elements(
                By.CLASS_NAME,
                'choice-set'
            )

            time.sleep(2)

            sel_model_selector = sel_choices[1].find_element(
                By.TAG_NAME,
                'select'
            )
            sel_model_options = sel_model_selector.find_elements(
                By.XPATH,
                './/*'
            )

            time.sleep(2)

            model_selector = Select(sel_model_selector)
        except Exception:
            self.logger.warning('Could not Select Model Type')
            return ([], [])

        return (model_selector, sel_model_options)

    def __extract_metadata_table(self) -> list:
        meta_data = []

        """GET ROWS OF DOWNLOAD TABLE"""
        try:
            sel_table = self.driver.find_element(By.CLASS_NAME, 'items-table')
            sel_body = sel_table.find_element(By.TAG_NAME, 'tbody')
            sel_rows = sel_body.find_elements(By.TAG_NAME, 'tr')
        except Exception:
            self.logger.debug(
                'Could not Extract Data from Table'
            )
            return []

        for i in range(0, len(sel_rows)):
            firmware_item = {
                "manufacturer": MANUFACTURER,
                "product_name": None,
                "product_type": None,
                "version": None,
                "release_date": None,
                "download_link": None,
                "checksum_scraped": None,
                "additional_data": {},
            }
            try:
                td = sel_rows[i].find_elements(By.TAG_NAME, 'td')

                if len(td) < 4:
                    self.logger.debug(
                        'Could not Scrape Firmware Row. Skip Firmware'
                    )
                    continue

                firmware_item['release_date'] = td[2].get_attribute(
                    'innerHTML'
                )

                firmware_item['version'] = td[1].get_attribute('innerHTML')

                """GET CHECKSUM"""
                try:
                    sel_download_elem = td[3].find_element(
                        By.CLASS_NAME,
                        'md5'
                    )

                    sel_md5 = sel_download_elem.find_element(
                        By.TAG_NAME,
                        'input'
                    )

                    firmware_item["checksum_scraped"] = sel_md5.get_attribute(
                        'value'
                    )
                except Exception:
                    self.logger.debug(attribute_scraping_failure("Checksum"))
                    firmware_item["checksum_scraped"] = None

                """DOWNLOAD LINK"""
                sel_tmp = td[3].find_element(By.CLASS_NAME, 'sources')
                sel_link_elem = sel_tmp.find_elements(By.TAG_NAME, 'li')
                firmware_item['download_link'] = sel_link_elem[0].find_element(
                    By.TAG_NAME,
                    'a'
                ).get_attribute('href')

                meta_data.append(firmware_item)
            except Exception:
                self.logger.debug(
                    'Could not Scrape Firmware Row from Table. Skip Firmware'
                )
                continue

        return meta_data

    def __loop_products(self):
        firmware = []

        try:
            (type_selector, sel_type_options) = self.__get_type_selector()
        except Exception:
            self.logger.error('Could not Get Product Type Selector.')
            return []

        self.logger.debug('Categorys Found -> ' + str(len(sel_type_options)))

        """LOOP THROUGH PRODUCT TYPE"""
        for i in range(1, len(sel_type_options)):
            type_selector.select_by_index(i)
            type_name = sel_type_options[i].get_attribute('innerHTML')

            try:
                (model_selector, sel_model_options) = self\
                    .__get_model_selector()
            except Exception:
                self.logger.warning('Could not Get Product Model Selector.')
                continue

            if len(sel_model_options) == 1:
                start_point = 0
                end_point = len(sel_model_options)
            else:
                start_point = 1
                end_point = len(sel_model_options) - 1

            """LOOP THROUGH PRODUCT MODEL"""
            for j in range(start_point, end_point):
                try:
                    model_selector.select_by_index(j)
                    model_name = sel_model_options[j]\
                        .get_attribute('innerHTML')

                    """SELECT AND SCRAPE FIRMWARE IF EXISTING"""
                    if self.__select_firmware():
                        time.sleep(4)
                        meta_data = self.__extract_metadata_table()

                        for m in meta_data:
                            m['product_type'] = type_name
                            m['product_name'] = model_name
                            self.logger.info(
                                firmware_scraping_success(
                                    f"{m['product_name']} {m['download_link']}")
                            )

                        firmware = firmware + meta_data

                        self.__scrape_cnt += 1

                        if self.__scrape_cnt == self.max_products:
                            return firmware

                except Exception:
                    self.logger.debug(
                        'Could not Scrape Product. Skip Product.'
                    )
                    continue
                time.sleep(1)

            time.sleep(2)

        return firmware

    def scrape_metadata(self) -> list:
        meta_data = []
        self.logger.important(start_scraping())
        self.logger.debug(
            'Scrape in Headless Mode Set -> '
            + str(self.headless)
        )

        self.logger.debug(
            'Max Products Set-> '
            + str(self.max_products)
        )

        self.__scrape_cnt = 0

        try:
            self.driver.get(self.scrape_entry_url)
            self.logger.info(
                entry_point_url_success(self.scrape_entry_url)
            )
        except Exception:
            self.logger.error(
                entry_point_url_failure(self.scrape_entry_url)
            )
            self.driver.quit()
            return []

        meta_data = self.__loop_products()

        self.logger.debug('Metadata Found -> ' + str(len(meta_data)))
        self.logger.important(finish_scraping())
        self.driver.quit()

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

    Scraper = QnapScraper(headless=False, driver=driver, max_products=50)
    print(json.dumps(Scraper.scrape_metadata()))
