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
import os
import json
from functools import partial, partialmethod
from pathlib import Path

# Add custom level "IMPORTANT" (between INFO and WARNING)
logging.IMPORTANT = 25
logging.addLevelName(logging.IMPORTANT, "IMPORTANT")
logging.Logger.important = partialmethod(logging.Logger.log, logging.IMPORTANT)
logging.important = partial(logging.log, logging.IMPORTANT)


class ColoredFormatter(logging.Formatter):

    reset = "\x1b[0m"
    grey = "\x1b[38;20m"
    cyan = "\x1b[36;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"

    format_prefix = "%(asctime)s - %(filename)14s:%(lineno)3d - "
    format_suffix = "%(levelname)9s - %(message)s"

    FORMATS = {
        logging.DEBUG: cyan + format_prefix + reset + grey + format_suffix + reset,
        logging.INFO: cyan + format_prefix + reset + grey + format_suffix + reset,
        logging.IMPORTANT: cyan + format_prefix + yellow + format_suffix + reset,
        logging.WARNING: cyan + format_prefix + yellow + format_suffix + reset,
        logging.ERROR: cyan + format_prefix + red + format_suffix + reset,
        logging.CRITICAL: cyan + format_prefix + bold_red + format_suffix + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger_name = "logger"
stream_level = logging.INFO
file_level = logging.INFO

# Set stream level according to env variable
log_levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "IMPORTANT": logging.IMPORTANT,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# Set stream level according to env variable / config.json
user_level = None
try:
    with open("src/config.json") as config_file:
        config = json.load(config_file)
    if config.get("log_level", None):
        user_level = config.get("log_level").upper()
except Exception as e:
    print(e)

# Env variable takes precedence over config.json
if os.getenv("LOG_LEVEL"):
    user_level = os.getenv("LOG_LEVEL").upper()

if user_level in ["DEBUG", "INFO", "IMPORTANT", "WARNING", "ERROR", "CRITICAL"]:
    stream_level = log_levels[user_level]
else:
    stream_level = log_levels["INFO"]


# Initialize logger
file_path = str(Path(__file__).parent) + "/logs.log"

root_logger = logging.getLogger(logger_name)
root_logger.setLevel(file_level)

file_handler = logging.FileHandler(file_path)
file_handler.setFormatter(ColoredFormatter())

stream_handler = logging.StreamHandler()
stream_handler.setLevel(stream_level)
stream_handler.setFormatter(ColoredFormatter())

root_logger.addHandler(file_handler)
root_logger.addHandler(stream_handler)


def get_logger():
    return logging.getLogger(logger_name)


# Functions for common log messages

# level: important
def start_scraping():
    """Use when scraping begins"""
    return "Started scraping"


# level: important
def finish_scraping():
    """Use when scraping finishes successfully"""
    return "Finished scraping"


# level: important
def abort_scraping():
    """Use when scraping is stopped prematurely due to an error"""
    return "Aborted scraping"


# level: info
def entry_point_url_success(url):
    """Use when driver.get() succeeds on the entry point URL"""
    return f"Successfully accessed entry point URL {url}"


# level: error
def entry_point_url_failure(url):
    """Use when driver.get() fails on the entry point URL"""
    return f"Could not access entry point URL {url}"


# (optional)
# level: debug
def firmware_url_success(url):
    """Typically not needed. Use when driver.get() succeeds on URL of firmware page"""
    return f"Successfully accessed firmware URL {url}"


# level: warning
def firmware_url_failure(url):
    """Use when driver.get() fails on URL of firmware page"""
    return f"Could not access firmware URL {url}"


# level: info
def firmware_scraping_success(string):
    """Use when db entry for a firmware product was successfully generated"""
    # string: product name and/or product url
    return f"Successfully scraped firmware {string}"


# level: warning
def firmware_scraping_failure(string):
    """Use when db entry for a firmware product could not be generated"""
    # string: product name and/or product url
    return f"Could not scrape firmware {string}"


# (optional)
# level: debug
def attribute_scraping_success(string):
    """Typically not needed. Use when one attribute of a db entry for a firmware product was successfully scraped"""
    return f"Successfully scraped {string}"


# level: warning when unexpected, debug when expected
def attribute_scraping_failure(string):
    """Use when one attribute of a db entry for a firmware product could not be scraped"""
    return f"Could not scrape {string}"
