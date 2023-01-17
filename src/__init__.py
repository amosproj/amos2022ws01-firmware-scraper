"""
modules need to be imported in this file to be accessible in core.py
"""

from src.db_connector import DBConnector
from src.scheduler import check_vendors_to_update
from src.logger import create_logger
