import time
import json
import re
from selenium.webdriver.common.by import By

from src.logger import *

HOME_URL = "https://www.netgear.com/support/"
BASE_URL = "https://www.netgear.com"
MANUFACTURER = "Netgear"

SEL_CHILD_XPATH = './*'


class NetgearScraper:
    def __init__(
        self,
        driver,
        scrape_entry_url: str = HOME_URL,
        headless: bool = True,
        max_products: int = float("inf")
    ):
        self.scrape_entry_url = scrape_entry_url
        self.name = MANUFACTURER
        self.logger = get_logger()
        self.max_products = max_products
        self.headless = headless
        self.__scrape_cnt = 0
        self.driver = driver

    def __get_download_elems(self, link: str) -> list:
        try:
            self.driver.get(link)
            sel_btn = self.driver.find_element(
                By.XPATH, '//a[@class="btn download"]')
            sel_btn.click()
            sel_download_elems = self.driver.find_elements(
                By.CLASS_NAME, 'accordion-item')
        except Exception as e:
            self.logger.error(
                "Could not Access Product Page. Skip Product"
                + "\n"
                + str(e))
            return []

        return sel_download_elems

    def __scrape_firmware(self, product_links: list) -> list:
        meta_data = []

        for i in product_links:
            self.logger.info('Scrape Product -> ' + i["product_name"])
            sel_download_elems = self.__get_download_elems(i["link"])
            file_amt = len(sel_download_elems)

            for j in range(0, file_amt):
                try:
                    time.sleep(1)
                    file_type = sel_download_elems[j].find_element(
                        By.TAG_NAME, 'h1').get_attribute('innerHTML')

                    if 'Firmware' not in file_type:
                        continue

                except Exception as e:
                    self.logger.warning(
                        'Could not select Firmware. Skip Firmware \n'
                        + str(e))
                    continue

                try:
                    sel_content = sel_download_elems[j].find_element(
                        By.CLASS_NAME, 'links')
                    download_link = sel_content.find_element(
                        By.TAG_NAME, 'a').get_attribute('href')

                    firmware_item = {
                        "manufacturer": "Netgear",
                        "product_name": i["product_name"],
                        "product_type": i["category"],
                        "version": file_type,
                        "release_date": None,
                        "download_link": download_link,
                        "checksum_scraped": None,
                        "additional_data": {},
                    }

                    meta_data.append(firmware_item)
                except Exception as e:
                    self.logger.warning(
                        'Cound not find Firmware Element. Skip Firmware \n'
                        + str(e))
                    continue

        return meta_data

    def __get_intern_product_link(self) -> list:
        links = []
        try:
            sel_product_section = self.driver.find_element(
                By.CLASS_NAME, 'intern-product-category')

            sel_section_childs = sel_product_section.find_elements(
                By.XPATH, SEL_CHILD_XPATH)
        except Exception as e:
            self.logger.error(
                'Abort. Could not Scrape Intern Product Links. -> \n' + str(e))
            return []

        for i in range(0, len(sel_section_childs)):
            try:
                cat_name = sel_section_childs[i]\
                    .find_element(By.CLASS_NAME, 'internal-product')\
                    .get_attribute('innerHTML')
                sel_product_intern = sel_section_childs[i]\
                    .find_element(By.CLASS_NAME,
                                  'product-category-product-intern')

                sel_childs = sel_product_intern\
                    .find_element(By.XPATH, SEL_CHILD_XPATH)\
                    .find_elements(By.XPATH, SEL_CHILD_XPATH)
            except Exception as e:
                self.logger.warning(
                    'Could not Scrape Intern Product Childs. -> \n' + str(e))
                continue

            for j in range(0, len(sel_childs)):
                try:
                    raw_link = sel_childs[j].get_attribute('onclick')

                    if not raw_link:
                        continue

                    link = BASE_URL + \
                        re.search("location.href='(.*)'", raw_link).group(1)

                    name = sel_childs[j].find_element(
                        By.CLASS_NAME, 'model').get_attribute('innerHTML')
                except Exception as e:
                    self.logger.warning(
                        'Could not Scrape Intern Product Link. -> \n' + str(e))
                    continue

                link_wrap = {
                    "category": cat_name,
                    "product_name": name,
                    "link": link
                }

                links.append(link_wrap)

                self.__scrape_cnt = self.__scrape_cnt + 1

                if self.__scrape_cnt == self.max_products:
                    return links

        return links

    def scrape_metadata(self) -> list:
        meta_data = []

        self.__scrape_cnt = 0

        self.logger.important('Start Scrape Vendor -> Netgear')
        self.logger.important(
            'Scrape in Headless Mode Set -> ' + str(self.headless))
        self.logger.important('Max Products Set-> ' + str(self.max_products))

        self.__scrape_cnt = 0

        self.logger.info(f'Start Scrape Vendor {MANUFACTURER}')

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

        links = self.__get_intern_product_link()
        meta_data = self.__scrape_firmware(links)

        self.logger.important(
            'Successfully Scraped Qnap Firmware -> ' + str(len(meta_data)))
        self.logger.info('Done.')
        self.driver.quit()

        return meta_data


if __name__ == "__main__":
    Scraper = NetgearScraper(get_logger(), headless=False, max_products=10)
    firmware_data = Scraper.scrape_metadata()
    with open("scraped_metadata/firmware_data_Netgear.json", "w") as firmware_file:
        json.dump(firmware_data, firmware_file)
