# Imports
import json
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from src.logger import create_logger

# logger = create_logger(level="INFO", name="test_scraper")
# logger.important(name=)


class RockwellScraper:
    def __init__(self, logger, max_products: int = float("inf"), headless: bool = True):
        self.login_url = (
            "https://compatibility.rockwellautomation.com/Pages/MyProfile.aspx"
        )
        self.url = "https://compatibility.rockwellautomation.com/Pages/MultiProductDownload.aspx"
        self.name = "Rockwell"
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
        self.driver.implicitly_wait(1)

        self.email = os.getenv("Rockwell_email", "")
        self.password = os.getenv("Rockwell_password", "")
        self.list_of_product_dicts = []

    def login(self):
        try:
            self.driver.get(self.login_url)
            username_element = self.driver.find_element(By.ID, "userNameInput")
            username_element.send_keys(self.email)

            password_element = self.driver.find_element(By.ID, "passwordInput")
            password_element.send_keys(self.password)
            password_element.send_keys(Keys.ENTER)
            self.logger.important("Successfully logged in!")
        except Exception as e:
            self.logger.warning("Could not log in!")
            raise (e)

    def get_all_products(self):
        try:
            self.driver.get(self.url)
            search_element = self.driver.find_element(
                By.XPATH, "//button[@onclick='MPS1.Search();']"
            )
            search_element.click()
            time.sleep(1)
            download_elements = self.driver.find_elements(
                By.XPATH, "//a[@class='tmpbs_list-group-item cstm-pt']"
            )
            text_elements = self.driver.find_elements(
                By.XPATH, "//span[@class='pull-right']"
            )
            # self.logger.info()
            return download_elements, text_elements
        except Exception as e:
            self.logger.warning("Could not find products!")
            raise (e)

    def start_scraping(self, download_elements: list, text_elements: list):
        # for t in range(0, len(text_elements), 2):
        if len(text_elements) > self.max_products:
            max_products = self.max_products
        else:
            max_products = len(text_elements)
        for t in range(0, max_products, 5):
            try:
                new_list_of_product_dicts = self.scrape_10_products(
                    download_elements, text_elements, t
                )
                self.list_of_product_dicts += new_list_of_product_dicts
            except Exception as e:
                self.logger.warning("Could not find products!")
                raise (e)

    def scrape_10_products(self, download_elements: list, text_elements: list, t: int):
        (
            prod_cats,
            prod_fams,
            prod_names,
            versions,
            download_links,
            list_of_product_dicts,
        ) = ([], [], [], [], [], [])

        for i in range(t, t + 5):
            if i > self.max_products:
                break
            try:
                text = text_elements[i].text
                prod_cat = text.split("/")[0].split("(")[-1]
                prod_fam = text.split("/")[1].split(")")[0]
                download_elements[i].click()

                active_version_elements = self.driver.find_elements(
                    By.XPATH,
                    "//a[@class='tmpbs_list-group-item cstm-pt tmpbs_text-center']",
                )
                # self.driver.implicitly_wait(5)
                if not active_version_elements:
                    prod_cats.append(prod_cat)
                    prod_fams.append(prod_fam)

                series_listing = self.driver.find_element(By.ID, "MPS1SeriesListing")
                if series_listing.text:
                    serieses = series_listing.text.split("\n")
                    for k in range(len(serieses)):
                        series_element = self.driver.find_element(
                            By.LINK_TEXT, serieses[k]
                        )
                        series_element.click()
                        time.sleep(0.3)
                        active_version_elements = self.driver.find_elements(
                            By.XPATH,
                            "//a[@class='tmpbs_list-group-item cstm-pt tmpbs_text-center']",
                        )
                        if not active_version_elements:
                            download_elements[i].click()
                        time.sleep(0.3)
                        for j in range(len(serieses) - 1, len(active_version_elements)):
                            if (
                                active_version_elements[j].get_attribute("title")
                                != "Retired"
                            ):
                                active_version_elements[j].click()
                                prod_cats.append(prod_cat)
                                prod_fams.append(prod_fam)
                            download_elements[i].click()
                            time.sleep(0.3)
                            self.driver.find_element(By.LINK_TEXT, serieses[k]).click()
                            time.sleep(0.3)
                            active_version_elements = self.driver.find_elements(
                                By.XPATH,
                                "//a[@class='tmpbs_list-group-item cstm-pt tmpbs_text-center']",
                            )
                            time.sleep(0.3)
                    continue

                for j in range(len(active_version_elements)):
                    download_elements[i].click()
                    time.sleep(0.5)
                    active_version_elements = self.driver.find_elements(
                        By.XPATH,
                        "//a[@class='tmpbs_list-group-item cstm-pt tmpbs_text-center']",
                    )
                    time.sleep(0.5)
                    if active_version_elements[j].get_attribute("title") != "Retired":
                        active_version_elements[j].click()
                        prod_cats.append(prod_cat)
                        prod_fams.append(prod_fam)
                        time.sleep(0.5)
            except:
                self.logger.warning("can't find " + text_elements[i].text)
                continue

        time.sleep(1)
        name_and_version_list = self.driver.find_element(
            By.ID, "MPS1CompareListing"
        ).text.split("\n")
        ids = (
            self.driver.find_element(By.ID, "MPS1VersionList")
            .get_attribute("value")
            .split(",")
        )

        for r in range(len(name_and_version_list)):
            download_links.append(
                "https://compatibility.rockwellautomation.com/Pages/MultiProductFindDownloads.aspx?crumb=112&refSoft=1&toggleState=&versions="
                + ids[r]
            )
            try:
                splitted_n_v = name_and_version_list[r].split("   ")
                prod_names.append(splitted_n_v[0].strip())
                versions.append(splitted_n_v[1].strip())
            except:
                splitted_n_v = name_and_version_list[r].split("  ")
                prod_names.append(splitted_n_v[0].strip())
                versions.append(splitted_n_v[1].strip())

        for t in range(len(prod_cats)):
            firmware_item = {
                "manufacturer": "Rockwell",
                "product_name": prod_names[t],
                "product_type": prod_cats[t],
                "version": versions[t],
                "download_link": download_links[t],
                "release_date": None,
                "checksum_scraped": None,
                "additional_data": {"product_family": prod_fams[t]},
            }
            list_of_product_dicts.append(firmware_item)
            self.logger.important(
                "Succesfully scraped " + prod_names[t] + " " + versions[t]
            )

        if prod_cats:
            trash_element = self.driver.find_element(By.ID, "MPS1TrashCmd")

            try:
                trash_element.click()
            except:
                download_elements[i].click()
                # time.sleep(0.3)
                trash_element.click()

        return list_of_product_dicts

    # def download_firmware(self, list_of_product_dicts):
    #  for prod_dict in list_of_product_dicts:
    #      self.driver.get(prod_dict["download_link"])

    def download_firmware(self, download_link: str):
        self.driver.get(download_link)
        firmware_only_elements = self.driver.find_elements(
            By.XPATH, "//span[contains(text(), 'Firmware Only')]"
        )
        for firmware_only_element in firmware_only_elements:
            firmware_only_element.click()

        cart_element = self.driver.find_element(
            By.XPATH, "//button[@onclick='cart.open();']"
        )
        cart_element.click()

        download_now_element = self.driver.find_element(
            By.XPATH, "//button[contains(text(), 'Download Now')]"
        )
        download_now_element.click()
        time.sleep(2)

        ok_element = self.driver.find_element(
            By.XPATH, "//button[contains(text(), 'Ok')]"
        )
        ok_element.click()
        time.sleep(2)

        download_now_element = self.driver.find_element(
            By.XPATH, "//button[contains(text(), 'Download Now')]"
        )
        download_now_element.click()
        time.sleep(2)

        accept_and_download_element = self.driver.find_element(
            By.XPATH, "//button[contains(text(), 'Accept and Download')]"
        )
        accept_and_download_element.click()

    def scrape_metadata(self) -> list[dict]:
        self.logger.important("Rockwell - Start scraping metadata of firmware products.")
        self.login()
        download_elements, text_elements = self.get_all_products()
        self.start_scraping(download_elements, text_elements)

        return self.list_of_product_dicts

# if __name__ == "__main__":
#
#     logger = create_logger()
#     RWS = Rockwell_Scraper(logger=logger)
#     RWS.login()
#     download_elements, text_elements = RWS.get_all_products()
#     RWS.start_scraping(download_elements, text_elements)
#     with open(r"C:\Users\Max\Documents\Master IIS\AMOS\amos2022ws01-firmware-scraper\src\Vendors\Rockwell\firmware2.json", "w") as fw_file:
#         json.dump(RWS.list_of_product_dicts, fw_file)
#     #RWS.download_firmware(RWS.list_of_product_dicts)f

# Rockwell	0	2023-01-08	2023-01-09	RockwellScraper

