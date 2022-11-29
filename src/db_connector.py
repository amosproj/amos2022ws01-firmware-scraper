"""
Module to connect to and interact with a local MySQL Server.

Currently, this module assumes that the MySQL server is running on the machine where it is executed.
Username and password for the server are provided by exporting the following environment variables:
MYSQL_USER
MYSQL_PASSWORD
"""
import json
import os

import mysql.connector
from mysql.connector import connect


class DBConnector:
    def __init__(self):
        self.db_user = os.getenv("MYSQL_USER")
        self.db_password = os.getenv("MYSQL_PASSWORD")

        # create firmware DB if it doesn't exist yet
        create_query = "CREATE DATABASE IF NOT EXISTS firmware;"
        try:
            with connect(
                user=self.db_user, password=self.db_password, host="127.0.0.1"
            ) as con:
                with con.cursor() as curser:
                    curser.execute(create_query)
        except Exception as ex:
            print(ex)

        # create product table if it doesn't exist yet
        create_products_table_query = """
                    CREATE TABLE IF NOT EXISTS products(
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        manufacturer VARCHAR(128),
                        product_name VARCHAR(255),
                        product_type VARCHAR(255),
                        version VARCHAR(64),
                        release_date DATE,
                        download_link VARCHAR(1024),
                        file_path VARCHAR(1024),
                        checksum_local CHAR(128),
                        checksum_scraped CHAR(128),
                        emba_tested BOOLEAN,
                        emba_report_path VARCHAR(1024),
                        embark_report_link VARCHAR(1024),
                        additional_data JSON
                    );
                """
        con = self._get_db_con()
        try:
            with con.cursor() as cursor:
                cursor.execute(create_products_table_query)
                con.commit()
        except Exception as ex:
            print(ex)
        finally:
            con.close()

    """Return a MySQLConnection to the firmware database."""

    def _get_db_con(self):
        config = {
            "user": self.db_user,
            "password": self.db_password,
            "host": "127.0.0.1",
            "database": "firmware",
        }
        try:
            con = mysql.connector.connect(**config)
        except Exception as ex:
            print(ex)
        else:
            return con

    """Expects dict of firmware metadata and returns tuple in expected format for insertion into DB."""

    def _convert_firmware_dict_to_tuple(self, fw_dict):
        return (
            fw_dict["manufacturer"],
            fw_dict["product_name"],
            fw_dict["product_type"],
            fw_dict["version"],
            fw_dict["release_date"],
            fw_dict["download_link"],
            # assumption: we first add to the db and download afterwards
            None,  # file_path
            None,  # checksum_local
            fw_dict["checksum_scraped"],
            None,  # emba_tested
            None,  # emba_report_path
            None,  # embark_report_link
            json.dumps(fw_dict["additional_data"]),
        )

    """
    Inserts a list of product records into the firmware table.
    
    Parameters:
    product_list (list[dict]): List of dicts, where every dict contains the metadata of a single
        scraped firmware. Expected keys: "manufacturer", "product_name", "product_type", 
        "version", "release_date", "download_link", "checksum_scraped", "additional_data". 
        Values can be Null.
    """

    def insert_products(self, product_list: list[dict]):
        insert_products_query = """
            INSERT INTO products
            (manufacturer, product_name, product_type, version, release_date, download_link, file_path, checksum_local,
             checksum_scraped, emba_tested, emba_report_path, embark_report_link, additional_data)
            VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        product_list = [
            self._convert_firmware_dict_to_tuple(fw_dict) for fw_dict in product_list
        ]
        con = self._get_db_con()
        try:
            with con.cursor() as cursor:
                cursor.executemany(insert_products_query, product_list)
                con.commit()
        except Exception as ex:
            print(ex)
        finally:
            con.close()

    """Returns all download links from the firmware table."""

    def retrieve_download_links(self):
        retrieve_links_query = """
            SELECT download_link, product_name
            FROM products;
        """
        con = self._get_db_con()
        try:
            with con.cursor() as cursor:
                cursor.execute(retrieve_links_query)
                result = cursor.fetchall()
        except Exception as ex:
            print(ex)
        finally:
            con.close()
        return result

    """Without argument: Returns all products from the firmware table else: manufacturer specific."""

    def get_products(self, manufacturer=""):
        retrieve_products_query = f"""
            SELECT *
            FROM products 
            WHERE 1=1
            """
        if manufacturer:
            # WHERE clause set to manufacturer string
            retrieve_products_query += f'AND manufacturer = "{manufacturer}";'
        else:
            retrieve_products_query += ";"
        con = self._get_db_con()
        try:
            # print(retrieve_products_query) # debug
            with con.cursor() as cursor:
                cursor.execute(retrieve_products_query)
                results = cursor.fetchall()
        except Exception as ex:
            print(ex)
        finally:
            con.close()
        return results


if __name__ == "__main__":
    db = DBConnector()

    with open("../test/files/firmware_data_schneider.json", "r") as file:
        test_data = json.loads(file.read())

    db.insert_products(test_data)

    print(*db.retrieve_download_links()[:5], sep="\n")
