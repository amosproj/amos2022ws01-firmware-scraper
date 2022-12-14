# Imports
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from src.logger import create_logger


class Rockwell_Scraper:
    def __init__(self, logger, max_products: int = float("inf"), headless: bool = False):
        self.login_url = "https://compatibility.rockwellautomation.com/Pages/MyProfile.aspx"
        self.url = "https://compatibility.rockwellautomation.com/Pages/MultiProductDownload.aspx"
        self.name = "Rockwell"
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        self.driver.implicitly_wait(1)

        self.logger = logger
        self.max_products: int = max_products
        self.headless: bool = headless
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--headless")

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
            search_element = self.driver.find_element(By.XPATH, "//button[@onclick='MPS1.Search();']")
            search_element.click()
            time.sleep(3)
            download_elements = self.driver.find_elements(
                By.XPATH, "//a[@class='tmpbs_list-group-item cstm-pt']"
            )
            text_elements = self.driver.find_elements(By.XPATH, "//span[@class='pull-right']")
            #self.logger.info()
            return download_elements, text_elements
        except Exception as e:
            self.logger.warning("Could not find products!")
            raise (e)

    def start_scraping(self, download_elements, text_elements):
        #for t in range(0, len(text_elements), 2):
        for t in range(0, 2, 2):
                try:
                    new_list_of_product_dicts = self.scrape_10_products(download_elements, text_elements, t)
                    self.list_of_product_dicts += new_list_of_product_dicts
                except Exception as e:
                    self.logger.warning("Could not find products!")
                    raise (e)


    def scrape_10_products(self, download_elements, text_elements, t):
        prod_cats, prod_fams, prod_names, versions, download_links, list_of_product_dicts = [], [], [], [], [], []

        for i in range(t, t + 2):
            text = text_elements[i].text
            prod_cat = text.split("/")[0].split("(")[-1]
            prod_fam = text.split("/")[1].split(")")[0]
            download_elements[i].click()

            active_version_elements = self.driver.find_elements(By.XPATH, "//a[@class='tmpbs_list-group-item cstm-pt tmpbs_text-center']")
            self.driver.implicitly_wait(5)
            if not active_version_elements:
                prod_cats.append(prod_cat)
                prod_fams.append(prod_fam)

            series_listing = self.driver.find_element(By.ID, "MPS1SeriesListing")
            if series_listing.text:
                serieses = series_listing.text.split("\n")
                for k in range(len(serieses)):
                    series_element = self.driver.find_element(By.LINK_TEXT, serieses[k])
                    series_element.click()
                    time.sleep(1)
                    active_version_elements = self.driver.find_elements(By.XPATH, "//a[@class='tmpbs_list-group-item cstm-pt tmpbs_text-center']")
                    time.sleep(1)
                    for j in range(len(serieses)-1, len(active_version_elements)):
                        if active_version_elements[j].get_attribute("title") != "Retired":
                            active_version_elements[j].click()
                            self.driver.implicitly_wait(5)
                            prod_cats.append(prod_cat)
                            prod_fams.append(prod_fam)
                        download_elements[i].click()
                        time.sleep(1)
                        self.driver.find_element(By.LINK_TEXT, serieses[k]).click()
                        time.sleep(1)
                        active_version_elements = self.driver.find_elements(By.XPATH, "//a[@class='tmpbs_list-group-item cstm-pt tmpbs_text-center']")
                        time.sleep(1)
                continue

            for j in range(len(active_version_elements)):
                download_elements[i].click()
                time.sleep(1)
                active_version_elements = self.driver.find_elements(By.XPATH, "//a[@class='tmpbs_list-group-item cstm-pt tmpbs_text-center']")
                time.sleep(1)
                if active_version_elements[j].get_attribute("title") != "Retired":
                    active_version_elements[j].click()
                    prod_cats.append(prod_cat)
                    prod_fams.append(prod_fam)
                    time.sleep(1)

        name_and_version_list = self.driver.find_element(By.ID, "MPS1CompareListing").text.split("\n")
        ids = self.driver.find_element(By.ID, "MPS1VersionList").get_attribute("value").split(",")

        for r in range(len(name_and_version_list)):
            download_links.append("https://compatibility.rockwellautomation.com/Pages/MultiProductFindDownloads.aspx?crumb=112&refSoft=1&toggleState=&versions=" + ids[r])
            try:
                splitted_n_v = name_and_version_list[r].split("   ")
                prod_names.append(splitted_n_v[0].strip())
                versions.append(splitted_n_v[1].strip())
            except:
                splitted_n_v = name_and_version_list[r].split("  ")
                prod_names.append(splitted_n_v[0].strip())
                versions.append(splitted_n_v[1].strip())
        trash_element = self.driver.find_element(By.ID, "MPS1TrashCmd")
        trash_element.click()

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

        return list_of_product_dicts

    def download_firmware(self, list_of_product_dicts):
        for prod_dict in list_of_product_dicts:
            self.driver.get(prod_dict["download_link"])
            firmware_only_elements = self.driver.find_elements(
                By.XPATH, "//span[contains(text(), 'Firmware Only')]"
            )
            for firmware_only_element in firmware_only_elements:
                firmware_only_element.click()

            cart_element = self.driver.find_element(By.XPATH, "//button[@onclick='cart.open();']")
            cart_element.click()

            download_now_element = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Download Now')]"
            )
            download_now_element.click()
            time.sleep(2)

            ok_element = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Ok')]")
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




if __name__ == "__main__":

    logger = create_logger()
    RWS = Rockwell_Scraper(logger=logger)
    RWS.login()
    download_elements, text_elements = RWS.get_all_products()
    RWS.start_scraping(download_elements, text_elements)
    RWS.download_firmware(RWS.list_of_product_dicts)


#
# firmware_item = {
#     "manufacturer": "SchneiderElectric",
#     "product_name": "title",
#     "product_type": "product_ranges",
#     "version": "version",
#     "release_date": "release_date",
#     "checksum_scraped": "None",
#     "additional_data": {"product_reference": "reference", "languages": "languages"},
# }
#
# prod_cats = []
# prod_fams = []
# prod_names = []
# versions = []
#
# text_elements = driver.find_elements(By.XPATH, "//span[@class='pull-right']")
# for t in range(0, len(text_elements), 10):
#     for i in range(t, t+10):
#         try:
#             text = text_elements[i].text
#             prod_cat = text.split("/")[0].split("(")[-1]
#             prod_fam = text.split("/")[1].split(")")[0]
#             download_elements[i].click()
#
#             active_version_elements = driver.find_elements(By.XPATH, "//a[@class='tmpbs_list-group-item cstm-pt tmpbs_text-center']")
#             #time.sleep(1)
#             driver.implicitly_wait(5)
#             if not active_version_elements:
#                 prod_cats.append(prod_cat)
#                 prod_fams.append(prod_fam)
#
#             series_listing = driver.find_element(By.ID, "MPS1SeriesListing")
#             if series_listing.text:
#                 serieses = series_listing.text.split("\n")
#                 for k in range(len(serieses)):
#                     series_element = driver.find_element(By.LINK_TEXT, serieses[k])
#                     series_element.click()
#                     time.sleep(1)
#                     active_version_elements = driver.find_elements(By.XPATH, "//a[@class='tmpbs_list-group-item cstm-pt tmpbs_text-center']")
#                     time.sleep(1)
#                     for j in range(len(serieses)-1, len(active_version_elements)):
#                         if active_version_elements[j].get_attribute("title") != "Retired":
#                             active_version_elements[j].click()
#                             driver.implicitly_wait(5)
#                             prod_cats.append(prod_cat)
#                             prod_fams.append(prod_fam)
#                         download_elements[i].click()
#                         time.sleep(1)
#                         driver.find_element(By.LINK_TEXT, serieses[k]).click()
#                         time.sleep(1)
#                         active_version_elements = driver.find_elements(By.XPATH, "//a[@class='tmpbs_list-group-item cstm-pt tmpbs_text-center']")
#                         time.sleep(1)
#                 continue
#
#             for j in range(len(active_version_elements)):
#                 download_elements[i].click()
#                 time.sleep(1)
#                 active_version_elements = driver.find_elements(By.XPATH, "//a[@class='tmpbs_list-group-item cstm-pt tmpbs_text-center']")
#                 time.sleep(1)
#                 if active_version_elements[j].get_attribute("title") != "Retired":
#                     active_version_elements[j].click()
#                     prod_cats.append(prod_cat)
#                     prod_fams.append(prod_fam)
#                     time.sleep(1)
#         except:
#             continue
#     name_and_version_element = driver.find_element(By.ID, "MPS1CompareListing")
#     name_and_versions = name_and_version_element.text
#     name_and_versions_list = name_and_versions.split("\n")
#     for name_and_version in name_and_versions_list:
#         try:
#             splitted_n_v = name_and_version.split("   ")
#             prod_names.append(splitted_n_v[0].strip())
#             versions.append(splitted_n_v[1].strip())
#         except:
#             splitted_n_v = name_and_version.split("  ")
#             prod_names.append(splitted_n_v[0].strip())
#             versions.append(splitted_n_v[1].strip())
#         print(name_and_version)
#
#     trash_element = driver.find_element(By.ID, "MPS1TrashCmd")
#     trash_element.click()
#
#     # print(name_and_version)
#
#
#
# download_button = driver.find_element(By.ID, "MPS1DownloadsTopCmd")
# download_button.click()
#
# firmware_only_elements = driver.find_elements(
#     By.XPATH, "//span[contains(text(), 'Firmware Only')]"
# )
# for firmware_only_element in firmware_only_elements:
#     firmware_only_element.click()
#
# cart_element = driver.find_element(By.XPATH, "//button[@onclick='cart.open();']")
# cart_element.click()
#
# download_now_element = driver.find_element(
#     By.XPATH, "//button[contains(text(), 'Download Now')]"
# )
# download_now_element.click()
# time.sleep(2)
#
# ok_element = driver.find_element(By.XPATH, "//button[contains(text(), 'Ok')]")
# ok_element.click()
# time.sleep(2)
#
# download_now_element = driver.find_element(
#     By.XPATH, "//button[contains(text(), 'Download Now')]"
# )
# download_now_element.click()
# time.sleep(2)
#
# accept_and_download_element = driver.find_element(
#     By.XPATH, "//button[contains(text(), 'Accept and Download')]"
# )
# accept_and_download_element.click()
#
# time.sleep(20)
#
#
#
# # dict_["manufacturer"].append("AVM")
# # dict_["product_name"].append(root.split("/")[1])
# # dict_["product_type"].append("NA")
# # dict_["version"].append("NA")
# # dict_["release_date"].append("NA")
# # dict_["checksum_scraped"].append("NA")
# # dict_["download_link"].append("NA")
# # dict_["additional_data"] = {}
#
#
# # Initialize variables
# driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
# api_header = {
#     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
# }
# op_sys = "Windows 10 64-bit"
#
#
# driver.get("https://compatibility.rockwellautomation.com/Pages/MyProfile.aspx")
# driver.implicitly_wait(5)
#
# username_element = driver.find_element(By.ID, "userNameInput")
# username_element.send_keys(email)
#
# password_element = driver.find_element(By.ID, "passwordInput")
# password_element.send_keys(password)
# password_element.send_keys(Keys.ENTER)