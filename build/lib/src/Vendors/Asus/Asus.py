'''
Scraper module for Asus vendor
'''

#
#
# #Imports
# from selenium import webdriver
# from selenium.webdriver.support.ui import Select
# from selenium.webdriver.common.by import By
# import requests
# import json
# import pandas as pd
#
# #Initialize variables
# exec_path = r"C:\Users\Max\Documents\Master IIS\AMOS\chromedriver_win32\chromedriver.exe"
# driver = webdriver.Chrome(executable_path = exec_path)
# api_header = {
#     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
# op_sys = "Windows 10 64-bit"
#
#
# def get_all_products():
#     product_types = []
#     product_series = []
#     produkt_links = []
#     all_products = {}
#     driver.get("https://www.asus.com/support/Download-Center/")
#     driver.implicitly_wait(3)
#
#     first_drp_element = driver.find_elements(By.CLASS_NAME, "select2")
#     all_options_1 = first_drp_element[0].text
#     all_options_1_list = all_options_1.split("\n")
#     all_options_1_list.remove("Product Type")
#     all_options_1_list.remove(" ------- Commercial -------")
#     #all_options_1_list.remove(" AIoT & Industrial Solutions")
#     all_options_1_list = all_options_1_list[3:4]
#
#     for i in range(len(all_options_1_list)):
#         print("1: " + all_options_1_list[i])
#         all_products[all_options_1_list[i]] = []
#         drp_1 = Select(first_drp_element[0])
#         driver.implicitly_wait(3)
#         drp_1.select_by_visible_text(all_options_1_list[i].strip())
#
#         driver.implicitly_wait(3)
#         second_drp_element = driver.find_elements(By.CLASS_NAME, "select2")
#         driver.implicitly_wait(3)
#         all_options_2 = second_drp_element[1].text
#         all_options_2_list = all_options_2.split("\n")
#         all_options_2_list.remove("Product Series")
#
#         for j in range(len(all_options_2_list)):
#             print("2: " + all_options_2_list[j])
#             all_products[all_options_1_list[i]].append(all_options_2_list[j])
#
#             drp_2 = Select(second_drp_element[1])
#             try:
#                 drp_2.select_by_visible_text(all_options_2_list[j].strip())
#             except:
#                 try:
#                     drp_2.select_by_visible_text(all_options_2_list[j])
#                 except:
#                     print("error --- did not find " + all_options_2_list[j])
#
#             element_1 = driver.find_element(By.CLASS_NAME, "vs__dropdown-toggle")
#             element_1.click()
#
#             element_2s = driver.find_elements(By.CLASS_NAME, "vs__dropdown-option")
#
#             options = []
#             for k in range(len(element_2s)):
#                 try:
#                     element_1.click()
#                     option = driver.find_element(By.ID, "vs1__option-" + str(k))
#                     option.click()
#                     option_link = driver.find_element(By.LINK_TEXT, "Driver & Utility")
#                     option_href = option_link.get_attribute("href")
#                     options.append(option_href[:-8] + "bios/")
#                     product_types.append(all_options_1_list[i])
#                     product_series.append(all_options_2_list[j])
#                     produkt_links.append(option_href[:-8] + "bios/")
#
#                 except:
#                     print("error --- did not find vs1__option-" + str(k))
#
#     df = pd.DataFrame({'product_types': product_types, 'product_series': product_series, 'produkt_links': produkt_links})
#     with open('all_products.json', 'w') as file:
#         json.dump(all_products, file)
#
#     final_product_types = []
#     final_product_series = []
#     product_names = []
#     versions = []
#     release_dates = []
#     download_links = []
#
#     #for l in range(len(df)):
#     for l in range(5):
#         url = df["produkt_links"].tolist()[l]
#         product_type = df["product_types"].tolist()[l]
#         product_series = df["product_series"].tolist()[l]
#
#         driver.get(url)
#
#         try:
#             product_name = driver.find_element(By.CLASS_NAME, "ProductSupportHeader__productTitle__2kwSv").text
#         except:
#             continue
#
#         try:
#             show_all_element = driver.find_element(By.CLASS_NAME, "ProductSupportDriverBIOS__expand__3J2jb")
#             show_all_element.click()
#         except:
#             pass
#
#         try:
#             download_elements = driver.find_elements(By.CLASS_NAME, 'ButtonRed__isDownload__1yVuk')
#             version_elements = driver.find_elements(By.CLASS_NAME, 'ProductSupportDriverBIOS__version__juFyd')
#             release_elements = driver.find_elements(By.CLASS_NAME, 'ProductSupportDriverBIOS__releaseDate__1jh2p')
#         except:
#             continue
#
#         for m in range(len(download_elements)):
#             final_product_types.append(product_type)
#             final_product_series.append(product_series)
#             product_names.append(product_name)
#             versions.append(version_elements[m].text.strip().split(" ")[1])
#             release_dates.append(release_elements[m].text.strip().split(" ")[0])
#             download_links.append(download_elements[m].get_attribute("href"))
#
#     final_df = pd.DataFrame({
#         "Product_type": final_product_types,
#         "Product_series": final_product_series,
#         "Product_name": product_names,
#         "Version": versions,
#         "Release_date": release_dates,
#         "Download_link": download_links,
#     })
#     print(final_df)
#     return final_df
#
#
#
# # def select_product(p_type, p_series):
# #     driver.get("https://www.asus.com/support/Download-Center/")
# #     driver.implicitly_wait(3)
# #
# #     first_drp_element = driver.find_elements(By.CLASS_NAME, "select2")
# #     drp_1 = Select(first_drp_element[0])
# #     drp_1.select_by_visible_text(p_type.strip())
# #
# #     second_drp_element = driver.find_elements(By.CLASS_NAME, "select2")
# #     drp_2 = Select(second_drp_element[1])
# #     drp_2.select_by_visible_text(p_series.strip())
# #
# #     element_1 = driver.find_element(By.CLASS_NAME, "vs__dropdown-toggle")
# #     element_1.click()
# #
# #     element_2s = driver.find_elements(By.CLASS_NAME, "vs__dropdown-option")
# #
# #     options = []
# #     for i in range(len(element_2s)):
# #         try:
# #             element_1.click()
# #             option = driver.find_element(By.ID, "vs1__option-" + str(i))
# #             option.click()
# #             option_link = driver.find_element(By.LINK_TEXT, "Driver & Utility")
# #             option_href = option_link.get_attribute("href")
# #             options.append(option_href[:-8] + "bios/")
# #         except:
# #             print("error --- did not find vs1__option-" + str(i))
# #
# #     return options
# #
# #
# # def get_download_url(model):
# #
# #     response = requests.get(
# #         'https://www.asus.com/support/api/product.asmx/GetPDSupportTab',
# #         headers = api_header,
# #         params = {'website': "global",
# #                 "ppid": "10286",
# #                 #"pdhashedid": "AC2ncaggy07MQy6A",
# #                 "model": model},
# #     )
# #     response_content = json.loads(response.content)["Result"]
# #     download_url = response_content["Obj"][0]["Items"][1]["Url"]
# #     return download_url
# #
# #
# # def get_download_links(op_sys, url):
# #     driver.get(url)
# #
# #     # drp_element = driver.find_element(By.ID, "selectOS")
# #     # driver.implicitly_wait(3)
# #     # drp = Select(drp_element)
# #     # driver.implicitly_wait(3)
# #     # drp.select_by_visible_text(op_sys)
# #     # driver.implicitly_wait(3)
# #
# #     show_all_element = driver.find_element(By.CLASS_NAME, "ProductSupportDriverBIOS__expand__3J2jb")
# #     show_all_element.click()
# #
# #     download_elements = driver.find_elements(By.CLASS_NAME, 'ButtonRed__isDownload__1yVuk')
# #     download_links = []
# #     for download_element in download_elements:
# #         download_links.append(download_element.get_attribute("href"))
# #     return download_links
# #
# #
# # def download_files(download_links):
# #     for url in download_links:
# #         driver.get(url)
#
# if __name__ == "__main__":
#     get_all_products()
#
#     # with open('all_products.json', 'r') as file:
#     #     all_products = json.load(file)
#     #     p_type = list(all_products.keys())[4]
#     #     p_series = all_products[p_type][1]
#     #
#     # options = select_product(p_type, p_series)
#     #
#     # #download_url = get_download_url(options[0])
#     # download_url = options[8]
#     # download_links = get_download_links(op_sys, download_url)
#     #
#     # download_files(download_links)