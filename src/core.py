"""
Core module for firmware scraper
"""

# Standard Libraries
import json
from urllib.request import urlopen

from tqdm import tqdm

from db_connector import DBConnector
from logger import create_logger
# Vendor Modules
from Vendors import AVMScraper, SchneiderElectricScraper, Synology_scraper


class Core:

    def __init__(self, vendor_list: list):
        self.vendor_list = vendor_list
        self.db = DBConnector()

    def get_product_catalog(self):
        print('Start scraping.')
        for vendor in self.vendor_list:
            print(f'Start {type(vendor).__name__}.')
            metadata = vendor.scrape_metadata()
            print(f'{type(vendor).__name__} done.')
            print(f'Insert {type(vendor).__name__} catalogue into DB.')
            self.db.insert_products(metadata)

    def compare_products(self):

        pass

    def download_firmware(self):
        print(f'Download firmware.')
        firmware = self.db.retrieve_download_links()
        for url, name in tqdm(firmware):
            save_as = f"../downloads/{name.replace('/', '-')}"
            with urlopen(url) as file:
                content = file.read()
            with open(save_as, 'wb') as out_file:
                out_file.write(content)
        print(f'Download done.')


if __name__ == '__main__':

    with open('config.json') as config_file:
        config = json.load(config_file)

    #core = Core([SchneiderElectricScraper(max_products=10)])
    core = Core([Synology_scraper()])
    core.get_product_catalog()
    core.download_firmware()
