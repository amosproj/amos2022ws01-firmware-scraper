"""
Core module for firmware scraper
"""


# Standard Libraries
import json
import os

from urllib.request import urlopen

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from src.db_connector import DBConnector
from src.scheduler import check_vendors_to_update, update_vendor_schedule
from src.logger import get_logger

# Vendor Modules
from src.Vendors import *

# Initialize logger and Options for selenium
logger = get_logger()
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--start-maximized")
options.add_argument("--window-size=1920,1080")


class Core:
    def __init__(self, logger):
        """Core class for firmware scraper

        Args:
            logger (_type_): logger
        """
        self.current_vendor = None
        self.logger = logger
        self.db = DBConnector()
        self.logger.info("Initialized core and DB.")

    def get_current_vendor(self):
        return self.current_vendor

    def set_current_vendor(self, new_vendor):
        self.current_vendor = new_vendor

    def get_product_catalog(self) -> bool:
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
            self.logger.error(
                f"Could not create temporary table for {self.current_vendor.name}."
            )
            self.logger.error(e)
            self.logger.important("Continue with next vendor.")
            return False

        try:
            # insert metadata into temporary table
            self.db.insert_products(metadata, table=f"{self.current_vendor.name}")
            self.logger.info(
                f"Inserted {self.current_vendor.name} catalogue into temporary table."
            )
        except Exception as e:
            self.logger.error(
                f"Could not insert {self.current_vendor.name} catalogue into temporary table."
            )
            self.logger.error(e)
            self.logger.important("Continue with next vendor.")
            return False

        return True

    def compare_products(self) -> bool:
        """compare products with historized products"""

        try:
            # compare products with historized products
            self.logger.info(
                f"Compare {self.current_vendor.name} catalogue with historized products."
            )
            metadata_new = self.db.compare_products(
                table1=f"{self.current_vendor.name}", table2="products"
            )
            self.logger.important(
                f"{len(metadata_new)} new products for {self.current_vendor.name}."
            )
        except Exception as e:
            self.logger.error(
                f"Could not compare {self.current_vendor.name} catalogue with historized products."
            )
            self.logger.error(e)
            self.logger.important("Continue with next vendor.")
            return False

        try:
            # insert new products into products table
            self.db.insert_products(metadata_new, table="products")
            self.logger.info(
                f"Inserted new products of {self.current_vendor.name} into products table."
            )
        except Exception as e:
            self.logger.error(
                f"Could not insert new products of {self.current_vendor.name} into products table."
            )
            self.logger.error(e)
            self.logger.important("Continue with next vendor.")
            return False

        try:
            # delete temporary table
            self.db.drop_table(table=f"{self.current_vendor.name}")
            self.logger.info(f"Dropped temporary table for {self.current_vendor.name}.")
        except Exception as e:
            self.logger.important(
                f"Could not drop temporary table for {self.current_vendor.name}."
            )
            self.logger.error(e)

        return True

    def download_firmware(self, download_dir):
        """download firmware from vendor"""
        vendor_name = self.get_current_vendor().name
        logger.important(f"Next: {vendor_name}")

        # (id, URL, file_path)
        download_links = self.db.get_download_links(vendor_name)
        # remove all URLs that have already been downloaded (file_path is not None)
        download_links = [item for item in download_links if item[2] is None]
        if len(download_links) == 0:
            logger.important(f"No new firmware to download for {vendor_name}.")
            return

        # Create vendor-specific download dir
        vendor_download_dir = os.path.join(download_dir, vendor_name)
        if not os.path.exists(vendor_download_dir):
            os.makedirs(vendor_download_dir)

        # Check if vendor implements specific download function
        vendor_download_func = getattr(self.current_vendor, "download_firmware", None)
        if callable(vendor_download_func):
            try:
                download_links = [item[:2] for item in download_links]
                self.current_vendor.download_firmware(download_links)
            except Exception as e:
                self.logger.warning(f"Could not finish downloading {vendor_name}.")
                self.logger.warning(e)
        else:
            num_downloads = len(download_links)

            for i, (id, url, _) in enumerate(download_links):
                try:
                    firmware_name = url.split("/")[-1].split("?")[0]
                    save_as = os.path.join(vendor_download_dir, firmware_name)
                    with urlopen(url) as file:
                        content = file.read()
                    with open(save_as, "wb") as out_file:
                        out_file.write(content)

                    self.db.set_file_path(id, save_as)
                    self.logger.info(
                        f"[{i+1}/{num_downloads}] Successfully downloaded {firmware_name}"
                    )
                except Exception as e:
                    self.logger.warning(
                        f"[{i+1}/{num_downloads}] Could not download {firmware_name}"
                    )
                    self.logger.warning(e)
        self.logger.important(f"Finished downloading firmware of {vendor_name}.")


if __name__ == "__main__":

    # load config (e.g. max_products, log_level, log_file, chrome settings, headless, etc.)
    # this way we can avoid boilerplate and hardcoding settings into every vendors module
    with open("src/config.json") as config_file:
        config = json.load(config_file)
    # get list of vendors to update
    vendor_and_max_products = check_vendors_to_update()
    vendors_to_scrape = [name for name, _ in vendor_and_max_products]
    logger.info(f"Scheduled scrapers: {str(vendors_to_scrape)}")

    # initialize core object
    core = Core(logger=logger)

    # iterate over vendors to update
    for vendor, max_products in vendor_and_max_products:
        logger.important(f"Next: {vendor}")

        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=options
            )
            glob = globals()
            core.set_current_vendor(
                globals()[vendor](max_products=max_products, driver=driver)
            )
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

        # prepare for EMBArk
        # core.prepare_for_embark()

        # cleaning, drop temporary tables if ERROR, etc.
        # core.cleaning()

        update_vendor_schedule(vendor)

    # Download firmware
    logger.important("Start firmware download.")
    try:
        download_dir = os.path.realpath(config["download_dir"])
        logger.important(f"Download directory: {download_dir}")
    except Exception as e:
        download_dir = os.path.realpath("../downloads")
        logger.important(
            f"Download directory not specified in config.json. Will download into '../downloads'."
        )

    for vendor, _ in vendor_and_max_products:
        try:
            # TODO we need the name attribute from the class
            # initialize with useless driver to make sure Object creation is successful
            # there is certainly a better way
            core.set_current_vendor(
                globals()[vendor](
                    max_products=None,
                    driver=webdriver.Chrome(
                        service=Service(ChromeDriverManager().install()),
                        options=options,
                    ),
                )
            )
            core.download_firmware(download_dir)
        except Exception as e:
            logger.warning(
                f"Could not finish downloading firmware of {core.get_current_vendor().name}."
            )
            core.logger.error(e)
            core.logger.important("Continue with next vendor.")
