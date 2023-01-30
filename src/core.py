"""
Core module for firmware scraper
"""


# Standard Libraries
import json
from urllib.request import urlopen

from tqdm import tqdm

from src.db_connector import DBConnector
from src.scheduler import check_vendors_to_update, update_vendor_schedule
from src.logger import get_logger

# Vendor Modules
from src.Vendors import *

# Initialize logger
logger = get_logger()


class Core:
    def __init__(self, logger):
        """Core class for firmware scraper

        Args:
            logger (_type_): logger
        """
        # self.current_vendor = current_vendor
        self.current_vendor = None
        self.logger = logger
        self.db = DBConnector()
        self.logger.info("Initialized core and DB.")

    def get_current_vendor(self):
        return self.current_vendor

    def set_current_vendor(self, new_vendor):
        self.current_vendor = new_vendor

    def get_product_catalog(self):
        """get product catalog from vendor"""
        # self.logger.important(f"Start scraping {self.current_vendor.name}.")

        try:
            # call vendor specific scraping function
            metadata = self.current_vendor.scrape_metadata()
            # self.logger.important(f"Scraping done. Insert {self.current_vendor.name} catalogue into temporary table.")
        except Exception as e:
            self.logger.error(f"Could not scrape {self.current_vendor.name}.")
            self.logger.error(e)
            self.logger.important("Continue with next vendor.")
            return False

        try:
            # create temporary table for current vendor
            self.db.create_table(table=f"{self.current_vendor.name}")
            self.logger.info(f"Created temporary table for {self.current_vendor.name}.")
        except Exception as e:
            self.logger.error(f"Could not create temporary table for {self.current_vendor.name}.")
            self.logger.error(e)
            self.logger.important("Continue with next vendor.")
            return False

        try:
            # insert metadata into temporary table
            self.db.insert_products(metadata, table=f"{self.current_vendor.name}")
            self.logger.info(f"Inserted {self.current_vendor.name} catalogue into temporary table.")
        except Exception as e:
            self.logger.error(f"Could not insert {self.current_vendor.name} catalogue into temporary table.")
            self.logger.error(e)
            self.logger.important("Continue with next vendor.")
            return False

        return True

    def compare_products(self):
        """compare products with historized products"""

        try:
            # compare products with historized products
            self.logger.info(f"Compare {self.current_vendor.name} catalogue with historized products.")
            metadata_new = self.db.compare_products(table1=f"{self.current_vendor.name}", table2="products")
            self.logger.important(f"{len(metadata_new)} new products for {self.current_vendor.name}.")
        except Exception as e:
            self.logger.error(f"Could not compare {self.current_vendor.name} catalogue with historized products.")
            self.logger.error(e)
            self.logger.important("Continue with next vendor.")
            return False

        try:
            # insert new products into products table
            self.db.insert_products(metadata_new, table="products")
            self.logger.info(f"Inserted new products of {self.current_vendor.name} into products table.")
        except Exception as e:
            self.logger.error(f"Could not insert new products of {self.current_vendor.name} into products table.")
            self.logger.error(e)
            self.logger.important("Continue with next vendor.")
            return False

        try:
            # delete temporary table
            self.db.drop_table(table=f"{self.current_vendor.name}")
            self.logger.info(f"Dropped temporary table for {self.current_vendor.name}.")
        except Exception as e:
            self.logger.important(f"Could not drop temporary table for {self.current_vendor.name}.")
            self.logger.error(e)

        return True

    def download_firmware(self):
        """download firmware from vendor"""
        vendor_download_func = getattr(self.current_vendor, "download_firmware", None)
        if callable(vendor_download_func):
            firmware = self.db.retrieve_download_links()
            self.current_vendor.download_firmware(firmware)
        else:
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
    # load config (e.g. max_products, log_level, log_file, chrome settings, headless, etc.)
    # this way we can avoid boilerplate and hardcoding settings into every vendors module
    with open("config.json") as config_file:
        config = json.load(config_file)

    # get list of vendors to update
    vendor_list = check_vendors_to_update()
    logger.info(f"Vendor list: {str(vendor_list)}")

    # initialize core object
    core = Core(logger=logger)

    # iterate over vendors to update
    for entry in vendor_list:
        vendor, max_products = entry
        logger.important(f"Next: {vendor}")

        try:
            core.set_current_vendor(globals()[vendor](max_products=max_products, logger=logger))
        except Exception as e:
            core.logger.error(f"Could not start {vendor}.")
            core.logger.error(e)
            core.logger.important("Continue with next vendor.")
            continue

        # scrape product catalog
        if not core.get_product_catalog():
            continue

        # compare products with historized products
        if not core.compare_products():
            continue

        # download firmware
        # core.download_firmware()

        # prepare for EMBArk
        # core.prepare_for_embark()

        # cleaning, drop temporary tables if ERROR, etc.
        # core.cleaning()

        update_vendor_schedule(vendor)