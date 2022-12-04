
import datetime
import json
import time
from urllib.request import urlopen

import schedule
from tqdm import tqdm

from db_connector import DBConnector
from logger import create_logger
from scheduler import check_schedule
from Vendors import AVMScraper, SchneiderElectricScraper

"""
Core module for firmware scraper
"""

# Standard Libraries


# Vendor Modules

# Initialize logger
logger = create_logger()

# Initialize vendor_dict
vendor_dict = {
    "AVM": AVMScraper(logger=logger),
    "Schneider": SchneiderElectricScraper(logger=logger, max_products=10)
}


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
            self.logger.important(
                f"Insert {type(vendor).__name__} catalogue into DB.")
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


def start_scheduler():
    vendor_list = check_schedule(logger=logger, vendor_dict=vendor_dict)

    core = Core(
        vendor_list=vendor_list,
        logger=logger,
    )
    core.get_product_catalog()


if __name__ == "__main__":

    schedule.every(5).seconds.do(start_scheduler)
    # schedule.every().day.at("00:00").do(check_schedule)
    while True:
        print("running --- " + str(datetime.datetime.now()))
        schedule.run_pending()
        time.sleep(1)
        # time.sleep(60)
