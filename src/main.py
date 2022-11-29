from scraper import Zyxel_Scraper
from zipfile import ZipFile

import pathlib as pl
import os
import keyboard
#import time
import io
import PyPDF2


VENDOR_URL = "https://www.zyxel.com/de/de/support/download"
DRIVER_PATH = "C:\\Users\\Admin\\Desktop\\amos\\chromedriver_win32\\chromedriver.exe"

# def http_head(url:str):
#     res = requests.head(url)
#     print(res.status_code)
#     print(res.headers)
    
# def get_files(folder):
#     import os
#     os.chdir(folder)
#     files = os.listdir()
#     files = [x for x in files if x.endswith(".pdf")]
#     return files 

# def create_txt_files(path, filename):
#     KILL_KEY = 'esc'
#     tmp = path + "\\" + filename
#     with open(tmp, "rb") as pdf_file:
#         read_pdf = PyPDF2.PdfFileReader(pdf_file)
#         number_of_pages = read_pdf.getNumPages()
#         print(number_of_pages)
#         for i in range(number_of_pages):
#             time.sleep(5)
#             page = read_pdf.pages[i]
#             page_content = page.extractText()
#             print(page_content)
        
#     return
    
# def file_unzip():
#     with ZipFile("C:\\Users\\Admin\\Desktop\\amos\\git\\amos2022ws01-firmware-scraper\\src\\GS1350-12HP_4.70(ABPJ.5)C0.zip", 'r') as zObject:
#         zObject.extractall(
#         path="C:\\Users\\Admin\\Desktop\\amos\\git\\amos2022ws01-firmware-scraper\\src\\temp")
        
#     files = get_files("C:\\Users\\Admin\\Desktop\\amos\\git\\amos2022ws01-firmware-scraper\\src\\temp")    

#     for i in files:
#         create_txt_files("C:\\Users\\Admin\\Desktop\\amos\\git\\amos2022ws01-firmware-scraper\\src\\temp", i)    

def main():
    Scraper = Zyxel_Scraper(DRIVER_PATH)
    Scraper.get_product_catalog()
    #download_links = Scraper.get_download_links()
    #[http_head(i) for i in download_links]
    #file_unzip()
    #print(Scraper.get_download_links())

if __name__ == "__main__":
    main()