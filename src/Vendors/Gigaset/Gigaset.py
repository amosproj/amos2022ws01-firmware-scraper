from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class GigasetScraper:
    def __init__(self, logger):
        self.url = "https://teamwork.gigaset.com/gigawiki/pages/viewpage.action?pageId=37486876"
        self.options = Options()
        self.name = "Gigaset"
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.catalog: list[dict] = []
        self.logger = logger
        self.max_products = int = float("inf")

    def connect_webdriver(self):
        try:
            self.driver.get(self.url)
            self.logger.info("Connected Successfully!")
        except Exception as e:
            self.logger.exception("Could not connect to Gigaset!")
            raise (e)

    # TODO: get release_date
    def scrape_metadata(self) -> list[dict]:
        self.connect_webdriver()

        logger.info("Scraping Gigaset Firmware.")
        download_elems = self.driver.find_elements(
            By.CSS_SELECTOR, ".columnMacro.conf-macro.output-block > span > a"
        )
        download_links = [e.get_attribute("href") for e in download_elems]

        logger.debug(f"Found {len(download_links)} download links.")
        for link in download_links:

            logger.info(f"Scraping {link}")
            self.driver.get(link)

            CASE_1 = self.driver.find_elements(
                By.CSS_SELECTOR, "a[data-linked-resource-type='attachment']"
            )
            CASE_2 = self.driver.find_elements(By.CSS_SELECTOR, ".external-link")

            self.driver.find_elements(
                By.CSS_SELECTOR, "li[title='Show all breadcrumbs']"
            )[0].click()

            product_type = self.driver.find_element(
                By.CSS_SELECTOR, "ol#breadcrumbs > li:nth-last-child(2)"
            ).get_attribute("innerText")

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

            if len(self.catalog) >= self.max_products:
                break

        return self.catalog

    def get_attributes_to_compare(self) -> list[str]:
        return self.catalog["version"]


if __name__ == "__main__":

    import json

    from src.logger import create_logger

    logger = create_logger()
    Gigaset = GigasetScraper(logger=logger)
    firmware_data = Gigaset.scrape_metadata()

    with open("scraped_metadata/firmware_data_Gigaset.json", "w") as firmware_file:
        json.dump(firmware_data, firmware_file)
