import logging
import coloredlogs
from pathlib import Path

def setup_logger(logging_file_path: Path = None, name: str = "scraper", loglevel="INFO", log_to_file: bool = False):
    if loglevel is None:
        loglevel = "INFO"
    if logging_file_path is None:
        logging_file_path = Path.cwd() / "logs"
        logging_file_name = logging_file_path / "logger.log"
        Path(logging_file_path).mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(loglevel)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(loglevel)
    # create formatter and add it to the handlers
    fmt = "%(asctime)s - %(name)s %(levelname)s %(funcName)s: %(message)s"
    if log_to_file is True:
        # create file handler which logs warning messages
        fh = logging.FileHandler(logging_file_name)
        fh.setLevel(loglevel)
        fh.setFormatter(logging.Formatter(fmt))
        logger.addHandler(fh)
    ch.setFormatter(logging.Formatter(fmt))
    logger.addHandler(ch)
    coloredlogs.install(level=loglevel, logger=logger, fmt=fmt)
    return logger
