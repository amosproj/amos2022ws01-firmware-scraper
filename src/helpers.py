"""Module independent helper functions"""
import json
from src.logger import get_logger

logger = get_logger()

# load config file (e.g. max_products, log_level, log_file, chrome settings, headless, vendors etc.)
# this way we can avoid boilerplate and hardcoding settings into every vendors module
def get_config():
    try:
        with open("config.json") as config_file:
            config = json.load(config_file)
    except Exception as e:
        logger.error(
            "Could not read in 'config.json'. This file must be present in the project's root directory."
        )
        logger.error(e)
    return config
