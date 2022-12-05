"""
Core module for firmware scraper
"""

# Standard Libraries
import json
from urllib.request import urlopen
import time
import math
import datetime
from tqdm import tqdm
import pandas as pd

from db_connector import DBConnector
from logger import create_logger

# Vendor Modules
from Vendors import AVMScraper, SchneiderElectricScraper, Synology_scraper


#Initialize logger
logger = create_logger()


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


def check_vendors_to_update(schedule_file):
    with open("config.json") as config_file:
        config = json.load(config_file)

    vendor_list = []

    now = datetime.datetime.now().date()
    schedule_file["Next_update"] = pd.to_datetime(schedule_file["Next_update"]).dt.date
    todays_schedule = schedule_file[schedule_file["Next_update"] <= now]

    for index, row in todays_schedule.iterrows():
        if math.isnan(row["max_products"]):
            vendor_list.append(globals()[row["Vendor_class"]](logger = logger))
        else:
            vendor_list.append(globals()[row["Vendor_class"]](logger = logger, max_products = int(row["max_products"])))

        next_update = row["Last_update"] + datetime.timedelta(days=row["Intervall"])
        schedule_file.at[index, "Last_update"] = now
        schedule_file.at[index, "Next_update"] = next_update

    schedule_file.to_excel("schedule.xlsx", index=False)

    return vendor_list


if __name__ == "__main__":
    schedule_file = pd.read_excel("schedule.xlsx")
    vendor_list = check_vendors_to_update(schedule_file = schedule_file)

    core = Core(
        vendor_list=vendor_list,
        logger=logger,
    )

    core.get_product_catalog()
