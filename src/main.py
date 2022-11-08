from scraper import Zyxel_Scraper
import requests

VENDOR_URL = "https://www.zyxel.com/de/de/support/download"
DRIVER_PATH = "C:\\Users\\Admin\\Desktop\\amos\\chromedriver_win32\\chromedriver.exe"

def http_head(url:str):
    res = requests.head(url)
    print(res.status_code)
    print(res.headers)

def main():
    Scraper = Zyxel_Scraper(VENDOR_URL, DRIVER_PATH)
    download_links = Scraper.get_download_links()
    [http_head(i) for i in download_links]
    #print(Scraper.get_download_links())

if __name__ == "__main__":
    main()