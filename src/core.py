"""
Core module for firmware scraper
"""

# Standard Libraries
import json

# Vendor Modules
from Vendors import AVMScraper, SchneiderElectricScraper
from src.db_connector import DBConnector


class Core:

    def __init__(self, vendor_list: list):
        self.vendor_list = vendor_list
        self.db = DBConnector()

    def get_product_catalog(self):
        for vendor in self.vendor_list:
            metadata = vendor.scrape_metadata()
            self.db.insert_products(metadata)

    def compare_products(self):
        pass

    def download_firmware(self):
        pass

if __name__ == '__main__':

    with open('config.json') as config_file:
        config = json.load(config_file)

    core = Core([SchneiderElectricScraper(max_products=10)])
    core.get_product_catalog()
