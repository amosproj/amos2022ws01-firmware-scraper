'''
Scraper module for Asus vendor
'''


#Imports
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import requests
import json


#Initialize variables
exec_path = r"C:\Users\Max\Documents\Master IIS\AMOS\chromedriver_win32\chromedriver.exe"
driver = webdriver.Chrome(executable_path = exec_path)
api_header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
op_sys = "Windows 10 64-bit"


def get_all_products():
    all_products = {}
    driver.get("https://www.asus.com/support/Download-Center/")
    driver.implicitly_wait(3)

    first_drp_element = driver.find_elements(By.CLASS_NAME, "select2")
    all_options_1 = first_drp_element[0].text
    all_options_1_list = all_options_1.split("\n")
    all_options_1_list.remove(" ------- Commercial -------")

    for i in range(len(all_options_1_list)-1):
        print("1: " + all_options_1_list[i])
        all_products[all_options_1_list[i]] = []
        drp_1 = Select(first_drp_element[0])
        drp_1.select_by_visible_text(all_options_1_list[i].strip())

        driver.implicitly_wait(3)
        second_drp_element = driver.find_elements(By.CLASS_NAME, "select2")
        driver.implicitly_wait(3)
        all_options_2 = second_drp_element[1].text
        all_options_2_list = all_options_2.split("\n")

        for j in range(len(all_options_2_list)-1):
            print("2: " + all_options_2_list[j])
            all_products[all_options_1_list[i]].append(all_options_2_list[j])
            drp_2 = Select(second_drp_element[1])
            drp_2.select_by_visible_text(all_options_2_list[j].strip())

    with open('all_products.json', 'w') as file:
        json.dump(all_products, file)


def select_product(p_type, p_series):
    driver.get("https://www.asus.com/support/Download-Center/")
    driver.implicitly_wait(3)

    first_drp_element = driver.find_elements(By.CLASS_NAME, "select2")
    driver.implicitly_wait(3)
    drp_1 = Select(first_drp_element[0])
    drp_1.select_by_visible_text(p_type.strip())

    driver.implicitly_wait(3)

    second_drp_element = driver.find_elements(By.CLASS_NAME, "select2")
    driver.implicitly_wait(3)
    drp_2 = Select(second_drp_element[1])
    drp_2.select_by_visible_text(p_series.strip())

    driver.implicitly_wait(3)
    element_1 = driver.find_element(By.CLASS_NAME, "vs__dropdown-toggle")
    driver.implicitly_wait(3)
    element_1.click()

    driver.implicitly_wait(3)
    element_2s = driver.find_elements(By.CLASS_NAME, "vs__dropdown-option")

    options = []
    for i in range(len(element_2s)):
        driver.implicitly_wait(3)
        try:
            element_1.click()
            driver.implicitly_wait(3)
            option = driver.find_element(By.ID, "vs1__option-" + str(i))
            driver.implicitly_wait(3)
            option.click()
            driver.implicitly_wait(3)
            option_link = driver.find_element(By.LINK_TEXT, "Driver & Utility")
            option_href = option_link.get_attribute("href")
            options.append(option_href[:-8] + "bios/")
        except:
            print("error --- did not find vs1__option-" + str(i))

    return options


def get_download_url(model):

    response = requests.get(
        'https://www.asus.com/support/api/product.asmx/GetPDSupportTab',
        headers = api_header,
        params = {'website': "global",
                "ppid": "10286",
                #"pdhashedid": "AC2ncaggy07MQy6A",
                "model": model},
    )
    response_content = json.loads(response.content)["Result"]
    download_url = response_content["Obj"][0]["Items"][1]["Url"]
    return download_url


def get_download_links(op_sys, url):
    driver.get(url)
    driver.implicitly_wait(3)

    # drp_element = driver.find_element(By.ID, "selectOS")
    # driver.implicitly_wait(3)
    # drp = Select(drp_element)
    # driver.implicitly_wait(3)
    # drp.select_by_visible_text(op_sys)
    # driver.implicitly_wait(3)

    show_all_element = driver.find_element(By.CLASS_NAME, "ProductSupportDriverBIOS__expand__3J2jb")
    driver.implicitly_wait(3)
    show_all_element.click()
    driver.implicitly_wait(3)

    download_elements = driver.find_elements(By.CLASS_NAME, 'ButtonRed__isDownload__1yVuk')
    download_links = []
    for download_element in download_elements:
        download_links.append(download_element.get_attribute("href"))
    return download_links


def download_files(download_links):
    for url in download_links:
        driver.get(url)

if __name__ == "__main__":
    #get_all_products()

    with open('all_products.json', 'r') as file:
        all_products = json.load(file)
        p_type = list(all_products.keys())[4]
        p_series = all_products[p_type][1]

    options = select_product(p_type, p_series)

    #download_url = get_download_url(options[0])
    download_url = options[8]
    download_links = get_download_links(op_sys, download_url)

    download_files(download_links)