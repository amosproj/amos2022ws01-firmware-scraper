import datetime
import math
import time

import pandas as pd

from src.logger import create_logger

# initialize logger
logger = create_logger()


def _check_vendors_to_update(
    schedule_file_path: str = "src/schedule.xlsx", logger=logger
) -> list:
    """check if vendors need to be updated

    Args:
        schedule_file (excel): excel file with schedule
        logger (logger module, optional): logger.  Defaults to logger.

    Returns:
        _type_: list of vendor objects
    """
    vendor_list = []
    schedule_file = pd.read_excel(schedule_file_path)
    now = datetime.datetime.now().date()
    schedule_file["Next_update"] = pd.to_datetime(schedule_file["Next_update"]).dt.date
    todays_schedule = schedule_file[schedule_file["Next_update"] <= now]

    for index, row in todays_schedule.iterrows():
        if math.isnan(row["max_products"]):
            vendor_list.append(row["Vendor_class"](logger=logger))
        else:
            vendor_list.append(
                row["Vendor_class"](
                    logger=logger, max_products=int(row["max_products"])
                )
            )

    return vendor_list


def check_vendors_to_update(
    schedule_file_path: str = "src/schedule.xlsx", logger=logger
) -> list:
    """check if vendors need to be updated

    Args:
        schedule_file (excel): excel file with schedule
        logger (logger module, optional): logger.  Defaults to logger.

    Returns:
        _type_: list of vendor objects
    """
    vendor_list = []
    schedule_file = pd.read_excel(schedule_file_path)
    now = datetime.datetime.now().date()
    schedule_file["Next_update"] = pd.to_datetime(schedule_file["Next_update"]).dt.date
    todays_schedule = schedule_file[schedule_file["Next_update"] <= now]

    for index, row in todays_schedule.iterrows():
        if math.isnan(row["max_products"]):
            vendor_list.append(row["Vendor_class"])
        else:
            vendor_list.append(row["Vendor_class"])

    return vendor_list


# TODO


def update_schedule(schedule_file_path: str = "src/schedule.xlsx", logger=logger):
    """update schedule file AFTER vendor finished

    Args:
        schedule_file_path (str, optional): _description_. Defaults to "schedule.xlsx".
        logger (_type_, optional): _description_. Defaults to logger.
    """
    schedule_file = pd.read_excel("src/schedule.xlsx")

    next_update = row["Last_update"] + datetime.timedelta(days=row["Intervall"])
    schedule_file.at[index, "Last_update"] = now
    schedule_file.at[index, "Next_update"] = next_update

    schedule_file.to_excel("src/schedule.xlsx", index=False)
    pass


if __name__ == "__main__":

    check_vendors_to_update()
