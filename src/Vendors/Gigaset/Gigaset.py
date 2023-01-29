from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from src.logger import *


class GigasetScraper:
    def __init__(self, max_products: int = float("inf")):
        self.url = "https://teamwork.gigaset.com/gigawiki/pages/viewpage.action?pageId=37486876"
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--window-size=1920,1080")
        self.name = "Gigaset"
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=self.options
        )
        self.catalog: list[dict] = []
        self.logger = get_logger()
        self.max_products = max_products

    def connect_webdriver(self):
        try:
            self.driver.get(self.url)
            self.logger.info(entry_point_url_success(self.url))
        except Exception as e:
            self.logger.error(entry_point_url_failure(self.url))
            raise (e)

    # TODO: get release_date
    def scrape_metadata(self) -> list[dict]:
        self.connect_webdriver()

        self.logger.important(start_scraping())
        download_elems = self.driver.find_elements(
            By.CSS_SELECTOR, ".columnMacro.conf-macro.output-block > span > a"
        )
        download_links = [e.get_attribute("href") for e in download_elems]

        for link in download_links:

            self.driver.get(link)

            CASE_1 = self.driver.find_elements(
                By.CSS_SELECTOR, "a[data-linked-resource-type='attachment']"
            )
            CASE_2 = self.driver.find_elements(By.CSS_SELECTOR, ".external-link")

            self.driver.find_elements(
                By.CSS_SELECTOR, "li[title='Show all breadcrumbs']"
            )[0].click()

            product_type = (
                self.driver.find_element(
                    By.CSS_SELECTOR, "ol#breadcrumbs > li:nth-last-child(2)"
                )
                .get_attribute("innerText")
                .lstrip()
            )

            if CASE_1:
                download_link = CASE_1[0].get_attribute("href")

            elif CASE_2:
                download_link = CASE_2[0].get_attribute("href")

            else:
                continue

            version = self.driver.find_elements(By.ID, "title-text")[0]
            version = version.get_attribute("innerText").split()[-1]

            firmware_item = {
                "manufacturer": "Gigaset",
                "product_name": product_type,
                "product_type": product_type,
                "version": version,
                "release_date": None,
                "download_link": download_link,
                "checksum_scraped": None,
                "additional_data": {},
            }

            self.catalog.append(firmware_item)
            self.logger.info(firmware_scraping_success(product_type + " " + version))

            if len(self.catalog) >= self.max_products:
                break
        self.logger.important(finish_scraping())
        return self.catalog


if __name__ == "__main__":

    import json

    Gigaset = GigasetScraper(max_products=10)
    firmware_data = Gigaset.scrape_metadata()

    with open("scraped_metadata/firmware_data_Gigaset.json", "w") as firmware_file:
        json.dump(firmware_data, firmware_file)
