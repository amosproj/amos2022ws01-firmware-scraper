'''
Logging module callable by all other moduels

Concept:
- Logger is set up in module logger.py
- Three different levels of log messages:
    - Info (mainly success messages, process started etc.)
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
    - Scanned product X - downloaded data
    - Scan finished - return to core

Either in core or vendor:
    - Download for product x succesful (file)
    - Summary for vendor to console (eg. 8/8 files have been downloaded)

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    - Timestamp
    - name --> filename (where does the log come from)
    - message needs to be formatted as well
'''


#Does not really work as planned yet
import logging

logger = logging.getLogger('logger_name')
#logger.setLevel(level)
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.WARNING)
logger.addHandler(console_handler)
file_handler = logging.FileHandler('logs.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)


logger.info("Test")