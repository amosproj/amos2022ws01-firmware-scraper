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
email = os.getenv("Honeywell_email", "")
password = os.getenv("Honeywell_password", "")


driver.get("https://hsmftp.honeywell.com/")
# driver.get("hwdm:aHR0cHM6Ly9oc21mdHBzb2Z0LmJsb2IuY29yZS53aW5kb3dzLm5ldDo0NDMvc29mdHdhcmVzL0JhcmNvZGUlMjBTY2FubmVycy9IYW5kaGVsZC8zODAwZ0hEJTIwTGluZWFyLUltYWdpbmclMjBTY2FubmVyL0N1cnJlbnQvMzU0ODAyMzQuWklQP3N2PTIwMTUtMDctMDgmc3I9YiZzaWc9M2FBY1EwQm8zeGdMWXdvdjdJYklZV0x4OTE5ZkNURVdpc0ZxVTZWSk82QSUzRCZzdD0yMDIyLTEyLTA2VDExJTNBNTklM0E0Nlomc2U9MjAyMi0xMi0wNlQxNyUzQTU5JTNBNDZaJnNwPXI=")
driver.implicitly_wait(3)

username_element = driver.find_element(By.ID, "identifierInput")
username_element.send_keys(email)

next_element = driver.find_element(By.ID, "postButton")
next_element.click()

password_element = driver.find_element(By.ID, "password")
password_element.send_keys(password)
password_element.send_keys(Keys.ENTER)

time.sleep(5)

expand_elements = driver.find_elements(By.XPATH, "//i[@role='presentation']")
for i in range(1, len(expand_elements), 2):
    expand_elements[i].click()

folder_elements = driver.find_elements(
    By.XPATH, "//button[@class='btn btn-link software-list__folderbutton']"
)
folder_elements[0].click()

folder_elements_2 = driver.find_elements(
    By.XPATH, "//button[@class='btn btn-link software-list__folderbutton']"
)
folder_elements_2[0].click()

folder_elements_3 = driver.find_elements(
    By.XPATH, "//button[@class='btn btn-link software-list__folderbutton']"
)
folder_elements_3[0].click()

folder_elements_4 = driver.find_elements(
    By.XPATH, "//button[@class='btn btn-link software-list__folderbutton']"
)
folder_elements_4[0].click()

folder_elements_5 = driver.find_elements(By.XPATH, "//button[@class='btn btn-link']")
folder_elements_5[0].click()
time.sleep(13)

# WebDriverWait(driver, 10).until(EC.alert_is_present())

# driver.find_element(By.LINK_TEXT, "Honeywell Software Downloader öffnen")
alert_obj = driver.switch_to.alert
alert_obj.accept()

x = 5
