"""
Core module for firmware scraper
"""

# Standard Libraries

# Vendor Modules
from Vendors import AVMScraper, schneider_electric

class Core:

    def __init__(self,
                vendor_list: list[str]):
        self.vendor_list = vendor_list

    def get_product_catalog(self):
        pass

    def compare_products(self):
        pass

    def download_firmware(self):
        pass

if __name__ == '__main__':

    # Standard Libraries
    import json

    with open('config.json') as config_file:
        config = json.load(config_file)
