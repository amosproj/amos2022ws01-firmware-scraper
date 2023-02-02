# Imports
import json
import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from src.logger import *
from tqdm import tqdm
from src.Vendors.scraper import Scraper


class RockwellScraper(Scraper):
    def __init__(self, driver, max_products: int = float("inf"), headless: bool = True):
        self.login_url = "https://compatibility.rockwellautomation.com/Pages/MyProfile.aspx"
        self.url = "https://compatibility.rockwellautomation.com/Pages/MultiProductDownload.aspx"
        self.name = "Rockwell"
        self.logger = get_logger()
        self.driver = driver
        self.max_products: int = max_products

        self.headless: bool = headless
        self.driver.implicitly_wait(1)

        self.email = os.getenv("Rockwell_email", "")
        self.password = os.getenv("Rockwell_password", "")
        self.list_of_product_dicts = []

    def login(self):
        try:
            try:
                self.driver.get(self.login_url)
                self.logger.important(
                    f"Successfully accessed entry point URL {self.login_url}")
            except:
                self.logger.error(entry_point_url_failure(self.login_url))
            username_element = self.driver.find_element(By.ID, "userNameInput")
            username_element.send_keys(self.email)

            password_element = self.driver.find_element(By.ID, "passwordInput")
            password_element.send_keys(self.password)
            password_element.send_keys(Keys.ENTER)
            self.logger.important("Successfully logged in!")
        except Exception as e:
            self.logger.error("Could not log in!")
            raise (e)

    def get_all_products(self):
        try:
            self.driver.get(self.url)
            search_element = self.driver.find_element(
                By.XPATH, "//button[@onclick='MPS1.Search();']")
            search_element.click()
            time.sleep(1)
            download_elements = self.driver.find_elements(
                By.XPATH, "//a[@class='tmpbs_list-group-item cstm-pt']")
            text_elements = self.driver.find_elements(
                By.XPATH, "//span[@class='pull-right']")
            self.logger.important(
                "Succesfully identified all product elements")
            return download_elements, text_elements
        except Exception as e:
            self.logger.warning("Could not find all product elements")
            raise (e)

    def start_scraping(self, download_elements: list, text_elements: list):
        # for t in range(0, len(text_elements), 2):
        if len(text_elements) > self.max_products:
            max_products = self.max_products
        else:
            max_products = len(text_elements)
        print(max_products)
        for t in range(0, max_products, 10):
            try:
                new_list_of_product_dicts = self.scrape_10_products(
                    download_elements, text_elements, t)
                self.list_of_product_dicts += new_list_of_product_dicts
            except Exception as e:
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

        for i in range(t, t + 10):
            if i > self.max_products:
                break
            try:
                text = text_elements[i].text
                prod_cat = text.split("/")[0].split("(")[-1]
                prod_fam = text.split("/")[1].split(")")[0]
                download_elements[i].click()
                self.driver.implicitly_wait(5)
                active_version_elements = self.driver.find_elements(
                    By.XPATH,
                    "//a[@class='tmpbs_list-group-item cstm-pt tmpbs_text-center']",
                )

                if not active_version_elements:
                    prod_cats.append(prod_cat)
                    prod_fams.append(prod_fam)

                series_listing = self.driver.find_element(
                    By.ID, "MPS1SeriesListing")
                if series_listing.text:
                    serieses = series_listing.text.split("\n")
                    for k in range(len(serieses)):
                        series_element = self.driver.find_element(
                            By.LINK_TEXT, serieses[k])
                        series_element.click()
                        time.sleep(0.5)
                        active_version_elements = self.driver.find_elements(
                            By.XPATH,
                            "//a[@class='tmpbs_list-group-item cstm-pt tmpbs_text-center']",
                        )
                        if not active_version_elements:
                            download_elements[i].click()
                        time.sleep(0.5)
                        for j in range(len(serieses) - 1, len(active_version_elements)):
                            if active_version_elements[j].get_attribute("title") != "Retired":
                                active_version_elements[j].click()
                                prod_cats.append(prod_cat)
                                prod_fams.append(prod_fam)
                            download_elements[i].click()
                            time.sleep(0.3)
                            self.driver.find_element(
                                By.LINK_TEXT, serieses[k]).click()
                            time.sleep(0.3)
                            active_version_elements = self.driver.find_elements(
                                By.XPATH,
                                "//a[@class='tmpbs_list-group-item cstm-pt tmpbs_text-center']",
                            )
                            time.sleep(0.5)
                        continue
                else:
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
                self.logger.warning(firmware_scraping_failure(
                    text_elements[i].text))
                continue

        time.sleep(1)
        try:
            name_and_version_list = self.driver.find_element(
                By.ID, "MPS1CompareListing").text.split("\n")
            try:
                name_and_version_list.remove(" ")
            except:
                pass
            ids = self.driver.find_element(
                By.ID, "MPS1VersionList").get_attribute("value").split(",")

            for r in range(len(name_and_version_list)):
                download_links.append(
                    "https://compatibility.rockwellautomation.com/Pages/MultiProductFindDownloads.aspx?crumb=112&refSoft=1&toggleState=&versions="
                    + ids[r]
                )
                try:
                    splitted_n_v = name_and_version_list[r].split("   ")
                    versions.append(splitted_n_v[1].strip())
                    prod_names.append(splitted_n_v[0].strip())
                except:
                    splitted_n_v = name_and_version_list[r].split("  ")
                    prod_names.append(splitted_n_v[1])
                    versions.append(splitted_n_v[2])

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
                self.logger.info(firmware_scraping_success(
                    f"{prod_names[t]} {versions[t]} {download_links[t]}"))

            if prod_cats:
                trash_element = self.driver.find_element(By.ID, "MPS1TrashCmd")

                try:
                    trash_element.click()
                except:
                    download_elements[i].click()
                    # time.sleep(0.5)
                    trash_element.click()
        except:
            pass

        return list_of_product_dicts

    def download_firmware(self, firmware):
        self.logger.important("Started downloading")
        for id, url in tqdm(firmware):
            self.driver.get(url)
            firmware_only_elements = self.driver.find_elements(
                By.XPATH, "//span[contains(text(), 'Firmware Only')]")
            for firmware_only_element in firmware_only_elements:
                firmware_only_element.click()

            cart_element = self.driver.find_element(
                By.XPATH, "//button[@onclick='cart.open();']")
            cart_element.click()

            download_now_element = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Download Now')]")
            download_now_element.click()
            time.sleep(2)

            ok_element = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Ok')]")
            ok_element.click()
            time.sleep(2)

            download_now_element = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Download Now')]")
            download_now_element.click()
            time.sleep(2)

            accept_and_download_element = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Accept and Download')]"
            )
            accept_and_download_element.click()
        self.logger.important("Finished downloading")

    def scrape_metadata(self) -> list[dict]:
        self.login()
        download_elements, text_elements = self.get_all_products()
        self.start_scraping(download_elements, text_elements)
        self.logger.important(finish_scraping())
#ToDO: Change path (delete src)
        with open(r"C:\Users\Max\Documents\Master IIS\AMOS\amos2022ws01-firmware-scraper\scraped_metadata\firmware_data_rockwell.json", "w") as firmware_file:
            json.dump(self.list_of_product_dicts, firmware_file)
        return self.list_of_product_dicts


if __name__ == "__main__":

    logger = get_logger()
    RWS = RockwellScraper(logger=logger)

    RWS.login()
    download_elements, text_elements = RWS.get_all_products()
    RWS.start_scraping(download_elements, text_elements)
# ToDO: Change path (delete src)
    with open("scraped_metadata/firmware_data_rockwell.json", "w") as firmware_file:
        json.dump(RWS.list_of_product_dicts, firmware_file)
