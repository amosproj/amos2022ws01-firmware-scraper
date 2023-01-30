"""
Module to connect to and interact with a local MySQL Server.

Currently, this module assumes that the MySQL server is running on the machine where it is executed.
Username and password for the server are provided via the config.json file, or, alternatively, 
by exporting the following environment variables, which take precedence over config.json:
MYSQL_USER
MYSQL_PASSWORD
"""
import json
import os
import datetime

import mysql.connector
from mysql.connector import connect
from src.logger import get_logger

logger = get_logger()

# if Docker flag set in ENV, run as Docker container
if os.getenv("DOCKER_PYTHON_SCRAPER"):
    HOST = "mysql_db"
else:
    HOST = "127.0.0.1"


def _get_mysql_user_password():
    try:
        with open("src/config.json") as config_file:
            config = json.load(config_file)
    except Exception as e:
        config = None

    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")

    if config:
        try:
            if not user:
                user = config["database"]["user"]
        except Exception as e:
            logger.error(
                "Could not retrieve mysql username from field ['database']['user'] of config.json. Username is also not set \
                 via environment variable MYSQL_USER."
            )
            logger.error(e)

        try:
            if not password:
                password = config["database"]["password"]
        except Exception as e:
            logger.error(
                "Could not retrieve mysql password from field ['database']['password'] of config.json. Password is also \
                not set via environment variable MYSQL_PASSWORD."
            )
            logger.error(e)

    return user, password


class DBConnector:
    def __init__(self):
        self.db_user, self.db_password = _get_mysql_user_password()

        # create firmware DB if it doesn't exist yet
        create_query = "CREATE DATABASE IF NOT EXISTS firmware;"
        try:
            with connect(
                user=self.db_user, password=self.db_password, host=HOST
            ) as con:
                with con.cursor() as curser:
                    curser.execute(create_query)
        except Exception as e:
            logger.error(
                "Could not connect to MYSQL database. Please check username and password."
            )
            logger.error(e)

        # create product table if it doesn't exist yet
        create_products_table_query = """
                    CREATE TABLE IF NOT EXISTS products(
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        inserted_at DATE,
                        manufacturer VARCHAR(128),
                        product_name VARCHAR(255),
                        product_type VARCHAR(255),
                        version VARCHAR(64),
                        release_date DATE,
                        download_link VARCHAR(1024),
                        product_url VARCHAR(1024),
                        file_path VARCHAR(1024),
                        checksum_local CHAR(128),
                        checksum_scraped CHAR(128),
                        emba_tested BOOLEAN,
                        emba_report_path VARCHAR(1024),
                        embark_report_link VARCHAR(1024),
                        runner_uuid CHAR(128),
                        additional_data JSON
                    );
                """
        con = self._get_db_con()
        try:
            with con.cursor() as cursor:
                cursor.execute(create_products_table_query)
                con.commit()
            con.close()
        except Exception as e:
            logger.error(
                "Could not connect to MYSQL database. Please check username and password."
            )
            logger.error(e)

    def _get_db_con(self):
        """Return a MySQLConnection to the firmware database."""
        config = {
            "user": self.db_user,
            "password": self.db_password,
            "host": HOST,
            "database": "firmware",
        }
        try:
            con = mysql.connector.connect(**config)
        except Exception as ex:
            print(ex)
        else:
            return con

    def _convert_firmware_dict_to_tuple(self, fw_dict):
        """Expects dict of firmware metadata and returns tuple in expected format for insertion into DB."""

        inserted_at = datetime.datetime.now().strftime("%Y-%m-%d")
        # TODO allow vendors to omit "product_url" during transition period
        product_url = fw_dict.get("product_url", None)

        return (
            inserted_at,
            fw_dict["manufacturer"],
            fw_dict["product_name"],
            fw_dict["product_type"],
            fw_dict["version"],
            fw_dict["release_date"],
            fw_dict["download_link"],
            product_url,
            # assumption: we first add to the db and download afterwards
            None,  # file_path
            None,  # checksum_local
            fw_dict["checksum_scraped"],
            None,  # emba_tested
            None,  # emba_report_path
            None,  # embark_report_link
            None,  # runner_uuid
            json.dumps(fw_dict["additional_data"]),
        )

    # debugging method
    def _execute_string(self, query: str):
        # TODO check if con.commit before or after fetchall
        """convenience method to execute a string query

        Args:
            query (str): query to execute

        Returns:
            result:
        """
        con = self._get_db_con()
        try:
            with con.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                con.commit()

        except Exception as ex:
            print(ex)
        finally:
            con.close()
        if result:
            return result

    def create_table(self, table: str):
        """creates table with given table name in DB Schema

        Args:
            table (str): table name as string for table to create
        """
        create_table_query = f"""CREATE TABLE IF NOT EXISTS {table}(
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        inserted_at DATE,
                        manufacturer VARCHAR(128),
                        product_name VARCHAR(255),
                        product_type VARCHAR(255),
                        version VARCHAR(64),
                        release_date DATE,
                        download_link VARCHAR(1024),
                        product_url VARCHAR(1024),
                        file_path VARCHAR(1024),
                        checksum_local CHAR(128),
                        checksum_scraped CHAR(128),
                        emba_tested BOOLEAN,
                        emba_report_path VARCHAR(1024),
                        embark_report_link VARCHAR(1024),
                        runner_uuid CHAR(128),
                        additional_data JSON
                    );
                """
        con = self._get_db_con()
        try:
            with con.cursor() as cursor:
                cursor.execute(create_table_query)
                con.commit()
        except Exception as ex:
            print(ex)
        finally:
            con.close()

    def drop_table(self, table: str):
        """drops table with given table name in DB Schema

        Args:
            table (str): table name as string for table to drop
        """
        drop_table_query = f"DROP TABLE IF EXISTS {table};"
        con = self._get_db_con()
        try:
            with con.cursor() as cursor:
                cursor.execute(drop_table_query)
                con.commit()
        except Exception as ex:
            print(ex)
        finally:
            con.close()

    def insert_products(self, product_list: list[dict], table: str = "products"):
        """
        Inserts a list of product records into the firmware table.

        Parameters:
        product_list (list[dict]): List of dicts, where every dict contains the metadata of a single
            scraped firmware. Expected keys: "manufacturer", "product_name", "product_type",
            "version", "release_date", "download_link", "checksum_scraped", "additional_data".
            Values can be Null.
        """
        insert_products_query = f"""
            INSERT INTO {table}
            (inserted_at, manufacturer, product_name, product_type, version, release_date, download_link, product_url, 
            file_path, checksum_local, checksum_scraped, emba_tested, emba_report_path, embark_report_link, runner_uuid, 
            additional_data)
            VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        try:
            # TODO this is seriously sketchy
            product_list = [
                self._convert_firmware_dict_to_tuple(fw_dict)
                for fw_dict in product_list
            ]
        except Exception as ex:
            print(ex)
        con = self._get_db_con()
        try:
            with con.cursor() as cursor:
                cursor.executemany(insert_products_query, product_list)
                con.commit()
        except Exception as ex:
            print(ex)
        finally:
            con.close()

    def retrieve_download_links(self, table: str = "products"):
        """Returns all download links from firmware table,

        Returns:
            result: download links as list of tuples
        """
        retrieve_links_query = f"""
            SELECT download_link, product_name
            FROM {table};
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

    def compare_products(self, table1: str, table2: str = "products") -> list[dict]:
        """Compares the given product catalog in DB with the products in the products table (historized) DB.
        arguments

        Args:
            table1 (str): table name of product catalog in temporary vendor table
            table2 (str, optional): table of of products table (historized). Defaults to 'products'.

        Returns:
            list[dict]: _description_
        """
        con = self._get_db_con()

        query = f"""select 
                    tmp.inserted_at, tmp.manufacturer, tmp.product_name, tmp.product_type, tmp.version, tmp.release_date, 
                    tmp.download_link, tmp.product_url, tmp.file_path, tmp.checksum_local,
                    tmp.checksum_scraped, tmp.emba_tested, tmp.emba_report_path, tmp.embark_report_link, tmp.runner_uuid,
                    tmp.additional_data
                    from {table1} as tmp left join {table2} as tmp2 
                    on tmp.product_name = tmp2.product_name 
                    and tmp.version = tmp2.version 
                    and tmp.manufacturer = tmp2.manufacturer 
                    and tmp.product_type = tmp2.product_type 
                    where tmp2.id is null;"""
        try:
            with con.cursor(dictionary=True) as cursor:
                # print(query) # Debug
                cursor.execute(query)
                result = cursor.fetchall()
        except Exception as ex:
            print(ex)
        finally:
            con.close()
        return result

    def get_products(self, manufacturer="", table="products"):
        """query DB for firmware on any table, optionally filtered by manufacturer

        Args:
            manufacturer (str, optional): get products filtered with WHERE clause on manufacturer. Defaults to ''.
            table (str, optional): table to query for firmwares. Defaults to 'products'.
        Returns:
            result: returns list of tuples with all products
        """

        retrieve_products_query = f"""
            SELECT *
            FROM {table}
            """
        if manufacturer:
            # WHERE clause set to manufacturer string
            retrieve_products_query += f'WHERE manufacturer = "{manufacturer}";'
        con = self._get_db_con()
        try:
            # print(retrieve_products_query)  # debug
            with con.cursor() as cursor:
                cursor.execute(retrieve_products_query)
                result = cursor.fetchall()
        except Exception as ex:
            print(ex)
        finally:
            con.close()
        return result


if __name__ == "__main__":
    db = DBConnector()

    with open("../scraped_metadata/firmware_data_schneider.json", "r") as file:
        test_data = json.loads(file.read())

    # insert schneider test_data into DB
    db.insert_products(test_data)
    # retrieve download links from compare schneider table
    # print(*db.retrieve_download_links(table='compare_schneider')[:5], sep="\n")

    # next test: drop and create table compare_schneider
    db._execute_string("DROP TABLE IF EXISTS compare_schneider;")
    db._execute_string("DROP TABLE IF EXISTS new_compare_schneider;")
    db.create_table(table="compare_schneider")
    db.create_table(table="new_compare_schneider")

    # insert schneider test_data into DB
    db.insert_products(test_data, table="compare_schneider")
    # change data and insert into schneider test_data into DB
    test_data[0]["version"] = "0.0.0"
    test_data[1]["version"] = "0.0.0"
    test_data[2]["version"] = "0.0.0"
    db.insert_products(test_data, table="new_compare_schneider")

    # print length of that table
    print(
        f""" unchanged length: {len(db.get_products(table="compare_schneider"))},
        changed length: {len(db.get_products(table="new_compare_schneider"))}"""
    )

    # compare schneider table with products table
    print(
        len(
            db.compare_products(
                table1="new_compare_schneider", table2="compare_schneider"
            )
        )
    )
