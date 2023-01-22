import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class BelkinScraper:
    def __init__(self, logger, max_products: int = float("inf")):
        self.url = "https://www.belkin.com/support-article/?articleNum=10807"
        self.options = Options()
        self.name = "Belkin"
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.catalog: list[dict] = []
        self.logger = logger
        self.max_products = max_products

    # TODO: handle missing firmware for some versions
    def connect_webdriver(self):
        try:
            self.driver.get(self.url)
            self.logger.info("Connected Successfully!")
        except Exception as e:
            self.logger.exception("Could not connect to Belkin!")
            raise (e)

    def scrape_metadata(self) -> list[dict]:
        self.connect_webdriver()
        prod_list = self.driver.find_elements(By.CSS_SELECTOR, "a[target='_blank']")
        prod_list = [
            e for e in prod_list if e.get_attribute("pathname") == "/support-article"
        ]
        link_list = [e.get_attribute("href") for e in prod_list][1:]
        ad_bar_clicked = False

        for link in link_list:
            self.driver.get(link)
            time.sleep(2)

            ad_bar = self.driver.find_elements(By.ID, "adroll_reject")

            if ad_bar and ad_bar_clicked == False:
                ad_bar[0].click()
                ad_bar_clicked = True

            product_name = self.driver.find_element(
                By.CLASS_NAME, "support-article__heading.h2.m-0"
            )

            product_name = product_name.get_attribute("innerText").split()[0]
            self.logger.info(f"Scraping product number: {product_name}")

            version_list = self.driver.find_elements(
                By.CSS_SELECTOR,
                "div#support-article-downloads > div.article-accordian.daccordion-is-closed",
            )
            self.logger.info(f"Found {len(version_list)} versions.")

            for i in range(len(version_list)):

                version = self.driver.find_elements(
                    By.CSS_SELECTOR, "div.article-accordian-content.collapse-me"
                )

                version = version[i].get_attribute("outerText").splitlines()[1]

                case_1 = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "div.article-accordian-content.collapse-me > span > span > a",
                )
                case_2 = self.driver.find_elements(
                    By.CSS_SELECTOR, "div.article-accordian-content.collapse-me > a"
                )

                case_3 = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "div.article-accordian-content.collapse-me > div > span > span > a",
                )

                case_4 = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "div.article-accordian-content.collapse-me > span > a",
                )

                fw_links = self.driver.find_elements(
                    By.CSS_SELECTOR, "a[href*='.bin'],[href*='.img']"
                )

                fw_links = [fw.get_attribute("href") for fw in fw_links]

                if not fw_links:
                    self.logger.info(
                        "Could not find firmware download links. Skipping."
                    )
                    break

                elif len(fw_links) != len(version_list):
                    logger.info("Could not find links for all versions. Skipping.")
                    break

                self.logger.info(f"Found {len(fw_links)} firmware downloads.")

                firmware_item = {
                    "manufacturer": "Belkin",
                    "product_name": product_name,
                    "product_type": product_name,
                    "version": version,
                    "release_date": None,
                    "download_link": fw_links[i],
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

    logger = create_logger(level="INFO")
    Belkin = BelkinScraper(logger=logger, max_products=1)
    firmware_data = Belkin.scrape_metadata()

    with open("scraped_metadata/firmware_data_Belkin.json", "w") as firmware_file:
        json.dump(firmware_data, firmware_file)
