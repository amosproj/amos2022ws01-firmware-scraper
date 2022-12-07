'''
Logging module callable by all other moduels

Concept:
- Logger is set up in module logger.py
- Three different levels of log messages:
    - Info (mainly success messages, processes started, finished etc.)
    - Warning (No dangerous errors, but something did not work as planned)
    - Error (All errors occuring)
- Two different handlers, one who logs to the console and one who logs to a log file
    - All information gets logged to file for a clear history - (levels: info, warning and error)
    - Important information gets logged to console - (levels: warning and error)

Logging in scheduler:
    - Scheduler started check_schedule (once per day)
    - Which vendors are scheduled for today
    - Handed vendor over to core

Logging in core:
    - Scan started vor vendor x
    - Scan finished for vendor x (return value recieved from vendor module); X new firmwares have been found and will be downloaded

Either in core or vendor:
    - Download for product x succesful (file)
    - Summary for vendor to console (eg. 8/8 files have been downloaded)

Logging in vendor modules:
    - Accesed main url (download center of vendor)
    - Vendor-depending messages like 'found url of product page',
    - Scanned product X - downloaded metadata
    - Scan finished - return to core

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    - Timestamp
    - name --> filename (where does the log come from)
    - message needs to be formatted as well


Message guide:
- Scheduler:
    - INFO - checking_schedule() started
    - INFO - checking schedule finished; the following vendors are schedules for today: vendor X, vendor Y, vendor Z
    - INFO - handed vendor x over to core
    - INFO - scheduled next scan for vendor X for xx.xx.xxxx

    - Warning -
    - ERROR -

- Core
    - INFO - Scan started for vendor X
    - INFO - Scan finished for vendor x; X new firmwares have been found and will be downloaded

    - INFO - Download for product x succesful (file) ToDO: How do we identify products in the logs? Name and vendor? ID?
    - WARNING - Summary for vendor to console (eg. 8/8 files have been downloaded)

- Vendor modules:
    - INFO - Accesed main url (download center of vendor)
    - INFO - scraped url of product page,
    - INFO - Scanned product X - downloaded metadata
    - INFO - Scan finished - return metadata  to core

    - IMPORTANT - Scan started in Vendor X.py
    - WARNING -


- Idea to move forward:
Since different vendors will create different problems, please check beforehand if a warning / error message for a new issue already exists here in the concept.
    - If yes: Use given structure
    - If not: add new message structure here
'''


import logging
from functools import partial, partialmethod
from pathlib import Path

# Add custom level "IMPORTANT" (between INFO and WARNING)
logging.IMPORTANT = 25
logging.addLevelName(logging.IMPORTANT, 'Important')
logging.Logger.important = partialmethod(logging.Logger.log, logging.IMPORTANT)
logging.important = partial(logging.log, logging.IMPORTANT)


def create_logger(level: str = "IMPORTANT"):
    if level == "INFO":
        con_level = logging.INFO
    else:
        con_level = logging.IMPORTANT

    file_path = str(Path(__file__).parent) + "/logs.log"

    logger = logging.getLogger("scraper")
    logger.setLevel(logging.INFO)

    format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler(file_path)
    file_handler.setFormatter(format)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(con_level)
    stream_handler.setFormatter(format)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
