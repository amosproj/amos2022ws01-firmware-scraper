"""
Core module for firmware scraper
"""


# Standard Libraries
import json
from urllib.request import urlopen

from tqdm import tqdm

from src.db_connector import DBConnector
from src.logger import create_logger
from src.scheduler import check_vendors_to_update

# Vendor Modules
from src.Vendors import *

# Initialize logger
# logger = create_logger("INFO")
logger = create_logger()


class Core:
    def __init__(self, current_vendor: Scraper, logger):
        """Core class for firmware scraper

        Args:
            current_vendor (str): current vendor
            logger (_type_): logger
        """
        self.current_vendor = current_vendor
        self.logger = logger
        # self.db = DBConnector()
        self.logger.important("Initialized core and DB.")

    def get_product_catalog(self):
        """get product catalog from vendor"""
        self.logger.important(f"Start scraping {self.current_vendor.name}.")

        # call vendor specific scraping function
        metadata = self.current_vendor.scrape_metadata()
        self.logger.important(
            f"Scraping done. Insert {self.current_vendor.name} catalogue into temporary table."
        )

        # create temporary table for current vendor
        self.db.create_table(table=f"{self.current_vendor.name}")
        self.logger.important(
            f"Created temporary table for {self.current_vendor.name}."
        )

        # insert metadata into temporary table
        self.db.insert_products(metadata, table=f"{self.current_vendor.name}")
        self.logger.important(
            f"Inserted catalogue into temporary table for {self.current_vendor.name}."
        )

    def compare_products(self):
        """compare products with historized products"""
        self.logger.important(
            f"Compare with historized products for {self.current_vendor.name}."
        )

        # compare products with historized products
        metadata_new = self.db.compare_products(
            table1=f"{self.current_vendor.name}", table2="products"
        )
        self.logger.important(
            f" {len(metadata_new)} new products for {self.current_vendor.name}."
        )

        # insert new products into products table
        self.db.insert_products(metadata_new, table="products")
        self.logger.important(
            f"Inserted new products into products for {self.current_vendor.name}."
        )

        # delete temporary table
        self.db.drop_table(table=f"{self.current_vendor.name}")
        self.logger.important(
            f"Dropped temporary table for {self.current_vendor.name}."
        )

    def download_firmware(self):
        """download firmware from vendor"""
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
    with open("src/config.json") as config_file:
        config = json.load(config_file)

    # get list of vendors to update
    vendor_list = check_vendors_to_update()
    logger.info(f"Vendor list: {str(vendor_list)}")

    # iterate over vendors to update
    for vendor in vendor_list:
        logger.info(f"Vendor: {vendor}")

        # initialize core class for each vendor
        core = Core(
            current_vendor=globals()[vendor](max_products=16, logger=logger),
            logger=logger,
        )

        # scrape product catalog
        core.get_product_catalog()

        # compare products with historized products
        core.compare_products()

        # download firmware
        # core.download_firmware()

        # prepare for EMBArk
        # core.prepare_for_embark()

        # cleaning, drop temporary tables if ERROR, etc.
        # core.cleaning()
