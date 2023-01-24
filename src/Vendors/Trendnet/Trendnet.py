from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

from loguru import logger as LOGGER
import json

HOME_URL = "https://www.trendnet.com/support/"
MANUFACTURER = "Trendnet"
DOWNLOAD_BASE_LINK = "https://www.trendnet.com/asp/download_manager/inc_downloading.asp?button=Continue+with+Download&Continue=yes&iFile="


class TrendnetScraper:
    def __init__(
        self,
        logger=LOGGER,
        scrape_entry_url: str = HOME_URL,
        headless: bool = True,
        max_products: int = float("inf")
    ):
        self.name = MANUFACTURER
        self.scrape_entry_url = scrape_entry_url
        self.logger = LOGGER
        self.__scrape_cnt = 0
        self.max_products = max_products
        self.headless = headless

        chromeOptions = webdriver.ChromeOptions()
        webdriver.ChromeOptions()

        if self.headless:
            chromeOptions.add_argument("--headless")
        chromeOptions.add_argument("--disable-dev-shm-using")
        chromeOptions.add_argument("--remote-debugging-port=9222")

        self.driver = webdriver.Chrome(
            options=chromeOptions, service=ChromeService(ChromeDriverManager()
                                                         .install()))

    def __get_product_download_links(self):
        self.logger.info('Scrape Product Links -> Start')

        try:
            selector = self.driver.find_element(By.NAME, "subtype_id")
            options = selector.find_elements(By.XPATH, ".//*")
        except Exception as e:
            self.logger.error('Could not find Product Selector -> ' + str(e))
            return []

        product_links = []

        for d in options:
            try:
                pname = d.get_attribute("innerHTML")
                path = d.get_attribute("value")
                if pname or path:
                    product = dict(name=d.get_attribute("innerHTML"),
                                   link=HOME_URL+d.get_attribute("value"))
                    product_links.append(product)
            except Exception as e:
                self.logger.error(
                    'Could not find Product Link. Skip Product -> ' + str(e))
                continue

        self.logger.info('Scrape Product Links -> Finished')
        return product_links

    # Extract Download link
    def __extract_download_link(self, to_extract: str) -> str:
        split = to_extract.rsplit(',')
        ifile = split[1].replace("'", "")

        downlod_link = DOWNLOAD_BASE_LINK + ifile
        return downlod_link

    # doesnt work properly bc some dates come in different format
    # convert date to Year-Month-Day
    def __convert_date(self, date_to_convert: str) -> str:
        splited_date = date_to_convert.split('/')

        if len(splited_date) < 2:
            return ''

        month = "0" + splited_date[0]
        year = splited_date[1]

        date = year + "-" + month + "-" + "01"

        return date

    def _scrape_product_data(self, p: dict) -> list:
        meta_data = []

        try:
            self.driver.get(p["link"])
            product_header = self.driver.find_element(By.ID, "product-header")

            if not product_header:
                self.logger.warning(
                    'Could not Scrape Product Firmware. Skip Product')
                return []

            product_type = product_header.find_element(
                By.XPATH, '/html/body/main/div[1]/div/div[2]/div/div[1]/h1')\
                .get_attribute('innerHTML').lstrip().strip()

            # get download links
            downloads = self.driver.find_element(By.ID, "downloads")

            if not downloads:
                self.logger.warning(
                    'Could not Scrape Product Firmware. Skip Product')
                return []

            cards = downloads.find_elements(By.CLASS_NAME, "card")
        except Exception as e:
            self.logger.warning(
                'Could not Scrape Product Firmware. Skip Product -> ' + str(e))
            return []

        for c in cards:
            firmware_item = {
                "manufacturer": "Trendnet",
                "product_name": None,
                "product_type": None,
                "version": None,
                "release_date": None,
                "download_link": None,
                "checksum_scraped": None,
                "additional_data": {},
            }

            try:
                header = c.find_element(By.CLASS_NAME, "card-header")
                data_type = header.get_attribute("innerHTML")

                if not data_type == "Firmware ":
                    continue

                row = c.find_element(By.CLASS_NAME, "row")
                tmp = row.find_element(By.TAG_NAME, "p")

                x = (tmp.text).splitlines()

                if len(x) < 2:
                    continue

                splited_version = x[0].rsplit(":")
                splited_release_date = x[1].rsplit(":")

                if len(splited_release_date) < 2 or len(splited_version) < 2:
                    continue

                version = splited_version[1]
                release_date = splited_release_date[1]
            except Exception as e:
                self.logger.warning(
                    'Could not Scrape Firmware. Skip Firmware -> ' + str(e))
                continue
            # find check sum
            try:
                check_sum = (
                    (row.find_element(By.CLASS_NAME, "g-font-size-13").text).rsplit(":"))[1]
            except Exception:
                check_sum = " "

            try:
                download_btn = row.find_element(By.CLASS_NAME, "btn")
                download_link = self.__extract_download_link(
                    download_btn.get_attribute('onclick'))
            except Exception as e:
                self.logger.warning(
                    'Could not Scrape Download link. Skip Firmware -> '
                    + str(e))

            firmware_item["product_name"] = p["name"]
            firmware_item["product_type"] = product_type
            firmware_item["version"] = version
            firmware_item["release_date"] = None
            #firmware_item["release_date"] = self.__convert_date(release_date)
            firmware_item["download_link"] = download_link
            firmware_item["checksum_scraped"] = check_sum.lstrip()

            meta_data.append(firmware_item)

        return meta_data

    def scrape_metadata(self) -> list:
        meta_data = []

        self.logger.info('Scrape Vendor Trendnet')
        self.logger.info('Headless -> ' + str(self.headless))
        self.logger.info('Max Products to Scrape -> ' + str(self.max_products))

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

        product_download_webpages = self.__get_product_download_links()

        if not product_download_webpages:
            self.logger.error('Abort. Could not find any Product Links')
            return []

        for p in product_download_webpages:
            scraped = self._scrape_product_data(p)
            meta_data = meta_data + scraped

            self.__scrape_cnt += 1

            if self.__scrape_cnt == self.max_products:
                break

        self.logger.info('Metadata Found -> ' + str(len(meta_data)))
        self.logger.info('Finished to Scrape -> Trendnet')
        self.driver.quit()
        return meta_data


def main():
    Scraper = TrendnetScraper(LOGGER, max_products=1)
    meta_data = Scraper.scrape_metadata()

    print(json.dumps(meta_data))


if __name__ == "__main__":
    main()
