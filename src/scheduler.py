'''
Scheduler module that starts core.py at predefined intervals
'''

import datetime
import pandas as pd
import json

schedule_file = pd.read_excel("schedule.xlsx")

def check_schedule(logger,  vendor_dict):
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

    return vendor_list