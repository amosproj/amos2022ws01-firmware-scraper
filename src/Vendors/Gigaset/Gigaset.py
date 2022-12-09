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

    def connect_webdriver(self):
        try:
            self.driver.get(self.url)
            self.logger.info("Connected Successfully!")
        except Exception as e:
            self.logger.exception("Could not connect to Gigaset!")
            raise (e)

    # TODO: navigate back and forth between sites
    def scrape_metadata(self) -> list[dict]:
        self.connect_webdriver()

        logger.info("Scraping Gigaset Firmware.")
        download_links = self.driver.find_elements(
            By.CSS_SELECTOR, ".confluence-embedded-image.image-right"
        )

        logger.debug(f"Found {len(download_links)} download links.")
        for link in download_links:

            logger.info(f"Scraping {link}")
            link.click()

            download_link = self.driver.find_elements(By.CLASS_NAME, "external-link")[
                0
            ].get_attribute("href")

            firmware_item = {
                "manufacturer": "Gigaset",
                "product_name": None,
                "product_type": None,
                "version": None,
                "release_date": None,
                "download_link": download_link if download_link else None,
                "checksum_scraped": None,
                "additional_data": {},
            }

            self.catalog.append(firmware_item)

            self.driver.get(self.url)

        return self.catalog

    def get_attributes_to_compare(self) -> list[str]:
        pass


if __name__ == "__main__":

    import json

    from utils import setup_logger

    logger = setup_logger()
    Gigaset = GigasetScraper(logger=logger)
    firmware_data = Gigaset.scrape_metadata()

    with open(
        "../../../scraped_metadata/firmware_data_Gigaset.json", "w"
    ) as firmware_file:
        json.dump(firmware_data, firmware_file)
