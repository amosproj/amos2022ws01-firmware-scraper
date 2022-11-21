'''
Logging module callable by all other moduels

Concept:
- Logger is set up in module logger.py
- Three different levels of log messages:
    - Info (mainly success messages, processes started, finished  etc.)
    - Warning (No dangerous errors, but something did not work as planned)
    - Error (All errors occuring)
- Two different handlers, one who logs to the console and one who logs to the file
    - All information gets logged to file for a clear history - (level info, warning and error)
    - Important information gets logged to console - (level warning and error)

Logging in scheduler:
    - Schedule started main (once per day)
    - Which vendors are schedules for today

Logging in core:
    - Scan started vor vendor x
    - Scan finished for vendor x (return value recieved from vendor module); X new firmwares have been found and will be downloaded

Logging in vendor modules:
    - Accesed main url (download center of vendor)
    - vendor-depending messages like 'found url of product page'
    - Scanned product X - downloaded metadata
    - Scan finished - return to core

Either in core or vendor:
    - Download for product x succesful (file)
    - Summary for vendor to console (eg. 8/8 files have been downloaded)

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    - Timestamp
    - name --> filename (where does the log come from)
    - message needs to be formatted as well
'''


import logging
from pathlib import Path

def create_logger(name):
    file_path = str(Path(__file__).parent) + "/logs.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler(file_path)
    file_handler.setFormatter(format)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(format)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger

logger = create_logger("logger.py")
logger.warning("logger warning Test")
logger.info("logger info Test")