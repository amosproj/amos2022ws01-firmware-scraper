"""
Core module for firmware scraper
"""

# Standard Libraries
import json
from urllib.request import urlopen

from tqdm import tqdm
from logger import create_logger
from db_connector import DBConnector

# Vendor Modules
from Vendors import AVMScraper, SchneiderElectricScraper


class Core:
    def __init__(self, vendor_list: list, logger):
        self.vendor_list = vendor_list
        self.logger = logger
        self.db = DBConnector()

    def get_product_catalog(self):
        self.logger.important("Start scraping.")
        for vendor in self.vendor_list:
            self.logger.important(f"Start {type(vendor).__name__}.")
            metadata = vendor.scrape_metadata()
            self.logger.important(f"{type(vendor).__name__} done.")
            self.logger.important(f"Insert {type(vendor).__name__} catalogue into DB.")
            self.db.insert_products(metadata)

    def compare_products(self):
        pass

    def download_firmware(self):
        self.logger.important("Download firmware.")
        firmware = self.db.retrieve_download_links()
        for url, name in tqdm(firmware):
            save_as = f"../downloads/{name.replace('/', '-')}"
            with urlopen(url) as file:
                content = file.read()
            with open(save_as, "wb") as out_file:
                out_file.write(content)
        self.logger.important("Download done.")


if __name__ == "__main__":

    with open("config.json") as config_file:
        config = json.load(config_file)

    logger = create_logger("scraper")

    core = Core(
        vendor_list=[
            AVMScraper(logger=logger),
            SchneiderElectricScraper(logger=logger, max_products=10),
        ],
        logger=logger,
    )
    core.get_product_catalog()
