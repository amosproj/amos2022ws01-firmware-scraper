'''
Scheduler module that starts core.py at predefined intervals
'''

import time
import schedule
import datetime
import pandas as pd
import json

from src.core import Core
from src.logger import create_logger
from src.Vendors import AVMScraper, SchneiderElectricScraper

#initialize logger
logger = create_logger()

schedule_file = pd.read_excel("schedule.xlsx")
vendor_dict={
    "AVM": AVMScraper(logger=logger),
    "Schneider": SchneiderElectricScraper(logger=logger, max_products=10)
    }


def check_schedule():
    with open("config.json") as config_file:
        config = json.load(config_file)
    vendor_list = []

    now = datetime.datetime.now().date()
    schedule_file["Next_update"] = pd.to_datetime(schedule_file["Next_update"]).dt.date
    todays_schedule = schedule_file[schedule_file["Next_update"] <= now]

    for index, row in todays_schedule.iterrows():
        vendor_list.append(vendor_dict[row["Vendor"]])
        next_update = row["Last_update"] + datetime.timedelta(days=row["Intervall"])
        schedule_file.at[index, "Last_update"] = now
        schedule_file.at[index, "Next_update"] = next_update

    schedule_file.to_excel("schedule.xlsx", index=False)

    core = Core(
        vendor_list,
        logger=logger,
    )
    core.get_product_catalog()


def start_scheduler():
    schedule.every(5).seconds.do(check_schedule)
    # schedule.every().day.at("00:00").do(check_schedule)
    while True:
        print("running --- " + str(datetime.datetime.now()))
        schedule.run_pending()
        time.sleep(1)
        # time.sleep(60)


if __name__ == "__main__":
    start_scheduler()