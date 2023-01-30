"""
module for scheduling and updating
"""
import datetime
import json


def check_vendors_to_update(config_file_path: str = "src/config.json") -> list:
    """check if vendors need to be updated

    Args:
        config_file_path (json): json file with schedule information
    Returns:
        _type_: list of tuples (vendor classname, max_products)
    """
    vendor_list = []
    with open(config_file_path, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    now = datetime.datetime.now().date()
    max_products_glob = config["max_products"]
    for vendor in config["vendors"]:
        if datetime.datetime.strptime(vendor["next_update"], "%Y-%m-%d").date() > now or not vendor["active"]:
            continue
        max_products = vendor["max_products"] if vendor["max_products"] else max_products_glob
        vendor_list.append((vendor["class_name"], max_products))
    return vendor_list


def update_vendor_schedule(vendor: str, config_file_path: str = "src/config.json"):
    """update schedule file AFTER vendor finished

    Args:
        vendor: str of vendor classname
        config_file_path (json): json file with schedule information
    """
    with open(config_file_path, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    now = datetime.datetime.now().date()
    for i in range(len(config["vendors"])):
        if config["vendors"][i]["class_name"] == vendor:
            config["vendors"][i]["last_update"] = now.strftime("%Y-%m-%d")
            config["vendors"][i]["next_update"] = (now + datetime.timedelta(
                days=int(config["vendors"][i]["interval"]))).strftime("%Y-%m-%d")
            break

    with open(config_file_path, "w", encoding="utf-8") as config_file:
        json.dump(config, config_file)


if __name__ == "__main__":
    update_vendor_schedule("DDWRTScraper")
    check_vendors_to_update()
