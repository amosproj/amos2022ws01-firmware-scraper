'''
Scheduler module that starts core.py at predefined intervals
'''

import time
import schedule
import datetime
import pandas as pd

from src import core

schedule_file = pd.read_excel("schedule.xlsx")

def create_product_catalog_demo(vendor):
    print(vendor)

def check_schedule():
    now = datetime.datetime.now().date()
    schedule_file["Next_update"] = pd.to_datetime(schedule_file["Next_update"]).dt.date
    todays_schedule = schedule_file[schedule_file["Next_update"] <= now]
    for index, row in todays_schedule.iterrows():
        #core.create_product_catalog(row["Vendor"])
        create_product_catalog_demo(row["Vendor"])

        # ToDo: check return value, if succesful ?
        next_update = row["Last_update"] + datetime.timedelta(days=row["Intervall"])
        schedule_file.at[index, "Last_update"] = now
        schedule_file.at[index, "Next_update"] = next_update

    schedule_file.to_excel("schedule.xlsx", index=False)

def start_scheduler():
    schedule.every(5).seconds.do(check_schedule)
    # schedule.every().day.at("00:00").do(check_schedule)
    while True:
        print("running --- " + str(datetime.datetime.now()))
        schedule.run_pending()
        time.sleep(1)
        #time.sleep(60)


if __name__ == "__main__":
    start_scheduler()