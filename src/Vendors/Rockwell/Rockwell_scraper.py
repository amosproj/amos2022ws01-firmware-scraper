# Imports
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Initialize variables
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
api_header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
}
op_sys = "Windows 10 64-bit"
email = os.getenv("Rockwell_email", "")
password = os.getenv("Rockwell_password", "")


driver.get("https://compatibility.rockwellautomation.com/Pages/MyProfile.aspx")
driver.implicitly_wait(3)

username_element = driver.find_element(By.ID, "userNameInput")
username_element.send_keys(email)

password_element = driver.find_element(By.ID, "passwordInput")
password_element.send_keys(password)
password_element.send_keys(Keys.ENTER)


driver.get(
    "https://compatibility.rockwellautomation.com/Pages/MultiProductDownload.aspx"
)
driver.implicitly_wait(3)

search_element = driver.find_element(By.XPATH, "//button[@onclick='MPS1.Search();']")
search_element.click()
time.sleep(3)

download_elements = driver.find_elements(
    By.XPATH, "//a[@class='tmpbs_list-group-item cstm-pt']"
)
first_download_element = download_elements[0]
first_download_element.click()

active_version_elements = driver.find_elements(By.XPATH, "//a[@title='Limited']")
for i in range(len(active_version_elements)):
    # time.sleep(1)
    active_version_elements = driver.find_elements(By.XPATH, "//a[@title='Limited']")
    active_version_elements[i].click()
    # time.sleep(1)
    first_download_element.click()

download_button = driver.find_element(By.ID, "MPS1DownloadsTopCmd")
download_button.click()

firmware_only_elements = driver.find_elements(
    By.XPATH, "//span[contains(text(), 'Firmware Only')]"
)
for firmware_only_element in firmware_only_elements:
    firmware_only_element.click()

cart_element = driver.find_element(By.XPATH, "//button[@onclick='cart.open();']")
cart_element.click()

download_now_element = driver.find_element(
    By.XPATH, "//button[contains(text(), 'Download Now')]"
)
download_now_element.click()
time.sleep(2)

ok_element = driver.find_element(By.XPATH, "//button[contains(text(), 'Ok')]")
ok_element.click()
time.sleep(3)

download_now_element = driver.find_element(
    By.XPATH, "//button[contains(text(), 'Download Now')]"
)
download_now_element.click()
time.sleep(3)

accept_and_download_element = driver.find_element(
    By.XPATH, "//button[contains(text(), 'Accept and Download')]"
)
accept_and_download_element.click()

time.sleep(20)
