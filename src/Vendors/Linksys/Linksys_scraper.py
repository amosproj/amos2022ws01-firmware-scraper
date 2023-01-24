# Imports
import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


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
        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options,
        )
        self.driver.implicitly_wait(3)
        self.list_of_product_dicts = []

    def get_all_product_urls(self):
        product_urls = []
        try:
            self.driver.get(self.url)
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
            self.logger.warning("Could not find product urls!")
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
                            info_p = version_parents[i].find_elements(By.TAG_NAME, "p")
                            if info_p:
                                download_link = (
                                    info_p[j]
                                    .find_element(By.TAG_NAME, "a")
                                    .get_attribute("href")
                                )
                                version = info_p[j].text.split("\n")[0].split(" ")[1]
                                release_date = datetime.datetime.strptime(
                                    info_p[j].text.split("\n")[1].split("  ")[1],
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
                                self.logger.important(
                                    "Succesfully scraped " + prod_name
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
                                self.logger.important(
                                    "Succesfully scraped " + prod_name
                                )

            except:
                self.logger.warning("Was not able to scrape " + prod_name)

    def scrape_metadata(self) -> list[dict]:
        self.logger.important("Linksys - Start scraping metadata of firmware products.")
        product_urls = self.get_all_product_urls()  #
        self.scrape_metadata_from_product_urls(product_urls)
        self.logger.important("Linksys - Succesfully scraped all metadata")
        return self.list_of_product_dicts

# if __name__ == "__main__":
#
#     logger = create_logger()
#     LS = LinksysScraper(logger=logger)
#
#     product_urls = LS.get_all_product_urls()#
#     LS.scrape_metadata_from_product_urls(product_urls)
