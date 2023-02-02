import time

from selenium.webdriver.common.by import By

from src.logger import *


class BelkinScraper:
    def __init__(self, driver, max_products: int = float("inf")):
        self.url = "https://www.belkin.com/support-article/?articleNum=10807"
        self.name = "Belkin"
        self.driver = driver
        self.catalog: list[dict] = []
        self.logger = get_logger()
        self.max_products = max_products
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.56 Safari/537.36"

    # TODO: handle missing firmware for some versions
    def connect_webdriver(self):
        try:
            self.driver.get(self.url)
            self.logger.info(entry_point_url_success(self.url))
        except Exception as e:
            self.logger.error(entry_point_url_failure(self.url))
            raise (e)

    def scrape_metadata(self) -> list[dict]:
        self.connect_webdriver()
        self.logger.important(start_scraping())
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
                try:
                    ad_bar[0].click()
                    ad_bar_clicked = True
                except Exception:
                    self.logger.error(error)

            product_name = self.driver.find_element(
                By.CLASS_NAME, "support-article__heading.h2.m-0"
            )

            product_name = product_name.get_attribute("innerText").split()[0]

            version_list = self.driver.find_elements(
                By.CSS_SELECTOR,
                "div#support-article-downloads > div.article-accordian.daccordion-is-closed",
            )

            for i in range(len(version_list)):

                version = self.driver.find_elements(
                    By.CSS_SELECTOR, "div.article-accordian-content.collapse-me"
                )

                version = version_list[i].get_attribute("outerText")

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
                    self.logger.warning(
                        firmware_scraping_failure(product_name + " " + version)
                    )
                    break

                elif len(fw_links) != len(version_list):
                    self.logger.warning(
                        firmware_scraping_failure(product_name + " " + version)
                    )
                    break

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

                self.logger.info(
                    firmware_scraping_success(product_name + " " + version)
                )

            if len(self.catalog) >= self.max_products:
                break

        self.logger.important(finish_scraping())

        return self.catalog


if __name__ == "__main__":

    import json

    Belkin = BelkinScraper(max_products=10)
    firmware_data = Belkin.scrape_metadata()

    with open("scraped_metadata/firmware_data_Belkin.json", "w") as firmware_file:
        json.dump(firmware_data, firmware_file)
