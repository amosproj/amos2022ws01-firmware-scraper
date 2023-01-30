# Imports
import datetime
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from src.logger import *
#from src.logger import get_logger
# import json


class LinksysScraper:
    def __init__(
        self, logger, max_products: int = float("inf"), headless: bool = True
    ):
        self.url = "https://www.linksys.com/sitemap"
        self.name = "Linksys"
        self.logger = logger
        self.max_products: int = max_products

        self.headless: bool = headless
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options,
        )
        self.driver.implicitly_wait(3)
        self.list_of_product_dicts = []

    def get_all_product_urls(self):
        product_urls = []
        try:
            try:
                self.driver.get(self.url)
                self.logger.important(entry_point_url_success(self.url))
            except:
                self.logger.error(entry_point_url_failure(self.url))
            product_elements = self.driver.find_elements(
                By.XPATH, "//a[@class='sitemap-list__link']"
            )
            if len(product_elements) > self.max_products:
                max_products = self.max_products
            else:
                max_products = len(product_elements)
            for i in range(max_products):
                product_url = product_elements[i].get_attribute("href")
                product_urls.append(product_url)
            self.logger.important("Succesfully scraped all product urls!")
            return product_urls
        except Exception as e:
            self.logger.error("Could not scrape all product urls!")
            raise (e)

    def scrape_metadata_from_product_urls(self, product_urls):
        for product_url in product_urls:
            try:
                self.driver.get(product_url)

                firmware_button = self.driver.find_elements(
                    By.LINK_TEXT, "DOWNLOADS / FIRMWARE"
                )
                if not firmware_button:
                    continue

                prod_name = self.driver.find_elements(
                    By.XPATH, "//div[@class='product-family-name h3']"
                )[0].text
                firmware_url = firmware_button[0].get_attribute("href")
                self.driver.get(firmware_url)

                version_clicks = self.driver.find_elements(
                    By.XPATH, "//div[@class='article-accordian daccordion-is-closed']"
                )
                version_parents = self.driver.find_elements(
                    By.XPATH, "//div[@class='article-accordian-content collapse-me']"
                )
                self.driver.implicitly_wait(3)
                for i in range(len(version_clicks)):
                    version_clicks[i].click()
                    titles = version_parents[i].find_elements(By.TAG_NAME, "h3")
                    time.sleep(0.5)
                    for j in range(len(titles)):
                        if "Firmware" in titles[j].text:
                            if titles[j].text in ["Firmware", "Firmware "]:
                                region_spec = "Firmware all regions"
                            else:
                                region_spec = titles[j].text
                            info_p = version_parents[i].find_elements(By.TAG_NAME, "p")
                            final_info_p = []
                            for p in info_p:
                                if p.text[0] == "V":
                                    final_info_p.append(p)
                            if final_info_p and len(final_info_p) > j:
                                download_link = (
                                    final_info_p[j]
                                    .find_element(By.TAG_NAME, "a")
                                    .get_attribute("href")
                                )
                                try:
                                    version = (
                                        final_info_p[j]
                                        .text.split("\n")[0]
                                        .split(" ")[1]
                                    )
                                except:
                                    version = final_info_p[j].text.split("\n")[0][4:]
                                try:
                                    release_date = datetime.datetime.strptime(
                                        final_info_p[j]
                                        .text.split("\n")[1]
                                        .split("  ")[1],
                                        "%m/%d/%Y",
                                    ).strftime("%d.%m.%Y")
                                except:
                                    release_date = final_info_p[j].text.split(
                                        "\n"
                                    )  # [1].split(" ")#[2]
                                    # release_date = datetime.datetime.strptime(
                                    #     info_p[j].text.split("\n")[1].split(" ")[2],
                                    #     "%m/%d/%Y",
                                    # ).strftime("%d.%m.%Y")
                                firmware_item = {
                                    "manufacturer": "Linksys",
                                    "product_name": prod_name,
                                    "product_type": None,
                                    "version": version,
                                    "download_link": download_link,
                                    "release_date": release_date,
                                    "checksum_scraped": None,
                                    "additional_data": {"region": region_spec},
                                }
                                self.list_of_product_dicts.append(firmware_item)
                                self.logger.info(
                                    firmware_scraping_success(
                                        f"{prod_name} {download_link}"
                                    )
                                )
                            else:
                                info_p = version_parents[i].find_elements(
                                    By.TAG_NAME, "div"
                                )
                                download_link = (
                                    info_p[j]
                                    .find_element(By.TAG_NAME, "a")
                                    .get_attribute("href")
                                )
                                version = info_p[j].text.split("\n")[1].split(" ")[1]
                                release_date = datetime.datetime.strptime(
                                    info_p[j].text.split("\n")[2].split(" ")[2],
                                    "%m/%d/%Y",
                                ).strftime("%d.%m.%Y")
                                firmware_item = {
                                    "manufacturer": "Linksys",
                                    "product_name": prod_name,
                                    "product_type": None,
                                    "version": version,
                                    "download_link": download_link,
                                    "release_date": release_date,
                                    "checksum_scraped": None,
                                    "additional_data": {},
                                }
                                self.list_of_product_dicts.append(firmware_item)
                                self.logger.info(
                                    firmware_scraping_success(
                                        f"{prod_name} {download_link}"
                                    )
                                )
            except:
                self.logger.warning(
                    firmware_scraping_failure(f"{prod_name} {download_link}")
                )

    def scrape_metadata(self) -> list[dict]:
        self.logger.important(start_scraping())
        product_urls = self.get_all_product_urls()
        self.scrape_metadata_from_product_urls(product_urls)
        self.logger.important(finish_scraping())
        return self.list_of_product_dicts


# if __name__ == "__main__":
#
#     logger = get_logger()
#
#     LS = LinksysScraper(logger=logger)#, max_products=5)
#
#     product_urls = LS.get_all_product_urls()
#     LS.scrape_metadata_from_product_urls(product_urls)
#     with open(
#         r"C:\Users\Max\Documents\Master IIS\AMOS\amos2022ws01-firmware-scraper\src\Vendors\Linksys\firmware.json", "w"
#     ) as fw_file:
#         json.dump(LS.list_of_product_dicts, fw_file)
