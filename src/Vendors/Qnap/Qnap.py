import time
import json
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from src.Vendors.scraper import Scraper
from src.logger import get_logger

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
                By.CLASS_NAME, 'download-type')
            sel_btns = sel_download_sec.find_elements(
                By.TAG_NAME, 'button')

            for i in range(0, len(sel_btns)):
                if 'Operating System' in sel_btns[i]\
                        .get_attribute('innerHTML'):
                    return True
        except Exception as e:
            self.logger.error(
                'Could not find Firmware Button Selector -> ' + str(e))
            return False

        return False

    def __get_type_selector(self):
        try:
            sel_selector = self.driver.find_element(By.CLASS_NAME, 'selector')
            sel_choices = sel_selector.find_elements(
                By.CLASS_NAME, 'choice-set')

            time.sleep(2)

            sel_type_selector = sel_choices[0].find_element(
                By.TAG_NAME, 'select')
            sel_type_options = sel_type_selector.find_elements(
                By.XPATH, './/*')

            time.sleep(2)

            type_selector = Select(sel_type_selector)
        except Exception as e:
            self.logger.error('Could not Select Product Type -> ' + str(e))
            return ([], [])

        return (type_selector, sel_type_options)

    def __get_model_selector(self):
        try:
            sel_selector = self.driver.find_element(By.CLASS_NAME, 'selector')
            sel_choices = sel_selector.find_elements(
                By.CLASS_NAME, 'choice-set')

            time.sleep(2)

            sel_model_selector = sel_choices[1].find_element(
                By.TAG_NAME, 'select')
            sel_model_options = sel_model_selector.find_elements(
                By.XPATH, './/*')
            time.sleep(2)

            model_selector = Select(sel_model_selector)
        except Exception as e:
            self.logger.error('Could not Select Model Type -> ' + str(e))
            return ([], [])

        return (model_selector, sel_model_options)

    def __extract_metadata_table(self) -> list:
        meta_data = []

        """GET ROWS OF DOWNLOAD TABLE"""
        try:
            sel_table = self.driver.find_element(By.CLASS_NAME, 'items-table')
            sel_body = sel_table.find_element(By.TAG_NAME, 'tbody')
            sel_rows = sel_body.find_elements(By.TAG_NAME, 'tr')
        except Exception as e:
            self.logger.error(
                'Could not Extract Data from Table -> \n' + str(e))
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
                    self.logger.error(
                        'Could not Scrape Firmware Row. Skip Firmware')
                    continue

                firmware_item['release_date'] = td[2].get_attribute(
                    'innerHTML')
                firmware_item['version'] = td[1].get_attribute('innerHTML')

                """GET CHECKSUM"""
                try:
                    sel_download_elem = td[3].find_element(
                        By.CLASS_NAME, 'md5')
                    sel_md5 = sel_download_elem.find_element(
                        By.TAG_NAME, 'input')
                    firmware_item["checksum_scraped"] = sel_md5.get_attribute(
                        'value')
                except Exception:
                    firmware_item["checksum_scraped"] = None

                """DOWNLOAD LINK"""
                sel_tmp = td[3].find_element(By.CLASS_NAME, 'sources')
                sel_link_elem = sel_tmp.find_elements(By.TAG_NAME, 'li')
                firmware_item['download_link'] = sel_link_elem[0].find_element(
                    By.TAG_NAME, 'a').get_attribute('href')

                meta_data.append(firmware_item)
            except Exception as e:
                self.logger.error(
                    'Could not Scrape Firmware Row from Table. Skip Firmware\n'
                    + str(e))
                continue

        return meta_data

    def __loop_products(self):
        firmware = []
        (type_selector, sel_type_options) = self.__get_type_selector()

        self.logger.info('Categorys Found -> ' + str(len(sel_type_options)))

        """LOOP THROUGH PRODUCT TYPE"""
        for i in range(1, len(sel_type_options)):
            type_selector.select_by_index(i)
            type_name = sel_type_options[i].get_attribute('innerHTML')

            (model_selector, sel_model_options) = self.__get_model_selector()

            self.logger.info('Products in -> (Category)' +
                             type_name + ' -> ' + str(len(sel_model_options)))

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

                        firmware = firmware + meta_data

                        self.__scrape_cnt += 1

                        if self.__scrape_cnt == self.max_products:
                            return firmware

                except Exception as e:
                    self.logger.error(
                        'Could not Scrape Product. Skip Product. \n', + str(e))
                    continue
                time.sleep(1)

            time.sleep(2)

        return firmware

    def scrape_metadata(self) -> list:
        meta_data = []
        self.logger.important('Start Scrape Vendor -> Qnap')
        self.logger.important(
            'Scrape in Headless Mode Set -> ' + str(self.headless))
        self.logger.important('Max Products Set-> ' + str(self.max_products))

        self.__scrape_cnt = 0

        self.logger.info('Start Scrape Vendor Qnap')

        try:
            self.driver.get(self.scrape_entry_url)
            self.logger.info(
                "Successfully accessed entry point URL " +
                self.scrape_entry_url)
        except Exception as e:
            self.logger.error(
                "Abort scraping. Could not access entry point URL -> "
                + str(e))
            self.driver.quit()
            return []

        meta_data = self.__loop_products()

        self.logger.important(
            'Successfully Scraped Qnap Firmware -> ' + str(len(meta_data)))
        self.logger.info('Done.')
        self.driver.quit()

        return meta_data


if __name__ == "__main__":
    Scraper = QnapScraper(get_logger(), headless=True, max_products=10)
    print(json.dumps(Scraper.scrape_metadata()))
