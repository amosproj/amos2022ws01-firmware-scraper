"""
Logging module

Concept:

- Five different levels of log messages:
    (see https://docs.python.org/3/howto/logging.html)

    - DEBUG (Detailed information, relevant to developers.)
    - INFO (Confirmation that things are working as expected - less important.)
    - IMPORTANT (Confirmation that things are working as expected - important.)
    - WARNING (Something unexpected happened, but the software continues to work.)
    - ERROR (All errors occurring.)

- Two different handlers, one who logs to the console and one who logs to a log file
    - Default:
        - All levels are logged to the logfile
        - Only levels >= INFO are logged to the console

"""

import logging
from functools import partial, partialmethod
from pathlib import Path

# Add custom level "IMPORTANT" (between INFO and WARNING)
logging.IMPORTANT = 25
logging.addLevelName(logging.IMPORTANT, "IMPORTANT")
logging.Logger.important = partialmethod(logging.Logger.log, logging.IMPORTANT)
logging.important = partial(logging.log, logging.IMPORTANT)

file_path = str(Path(__file__).parent) + "/logs.log"

root_logger = logging.getLogger("logger")
root_logger.setLevel(logging.INFO)

format = logging.Formatter("%(asctime)s - %(mod_name)s - %(levelname)s - %(message)s")

file_handler = logging.FileHandler(file_path)
file_handler.setFormatter(format)

con_level = logging.INFO
stream_handler = logging.StreamHandler()
stream_handler.setLevel(con_level)
stream_handler.setFormatter(format)

root_logger.addHandler(file_handler)
root_logger.addHandler(stream_handler)


class Logger:
    def __init__(self, mod_name: str):
        self.logger = root_logger
        self.mod_name = mod_name
        self.extra_dict = {"mod_name": self.mod_name}

    ### Common vendor functions
    # Vendor modules: use these whenever possible

    def start_scraping(self):
        """Use when scraping begins"""
        self.important("Started scraping")

    def finish_scraping(self):
        """Use when scraping finishes successfully"""
        self.important("Finished scraping")

    def abort_scraping(self):
        """Use when scraping is stopped prematurely due to an error"""
        self.important("Aborted scraping")

    def entry_point_url_success(self, string):
        """Use when driver.get() succeeds on the entry point URL"""
        self.info(f"Successfully accessed entry point URL {string}")

    def entry_point_url_failure(self, string):
        """Use when driver.get() fails on the entry point URL"""
        self.error(f"Could not access entry point URL {string}")

    # (optional)
    def firmware_url_success(self, url):
        """Typically not needed. Use when driver.get() succeeds on URL of firmware page"""
        self.debug(f"Successfully accessed firmware URL {url}")

    def firmware_url_failure(self, url):
        """Use when driver.get() fails on URL of firmware page"""
        self.warning(f"Could not access firmware URL {url}")

    def firmware_scraping_success(self, string):
        """Use when db entry for a firmware product was successfully generated"""
        # string: product name and/or product url
        self.info(f"Successfully scraped firmware of {string}")

    def firmware_scraping_failure(self, string):
        """Use when db entry for a firmware product could not be generated"""
        # string: product name and/or product url
        self.warning(f"Could not scrape firmware of {string}")

    # (optional)
    def attribute_scraping_success(self, string):
        """Typically not needed. Use when one attribute of a db entry for a firmware product was successfully scraped"""
        self.debug(f"Successfully scraped {string}")

    def attribute_scraping_failure(self, string):
        """Use when one attribute of a db entry for a firmware product could not be scraped"""
        self.warning(f"Could not scrape {string}")

    ### Wrapper functions
    # Vendor modules: only use for isolated cases

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs, extra=self.extra_dict)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs, extra=self.extra_dict)

    def important(self, msg, *args, **kwargs):
        self.logger.important(msg, *args, **kwargs, extra=self.extra_dict)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs, extra=self.extra_dict)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs, extra=self.extra_dict)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs, extra=self.extra_dict)
