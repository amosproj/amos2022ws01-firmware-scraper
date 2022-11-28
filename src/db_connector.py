"""
Module to connect to and interact with a local MySQL Server.

Currently, this module assumes that the MySQL server is running on the machine where it is executed.
Username and password for the server are provided by exporting the following environment variables:
MYSQL_USER
MYSQL_PASSWORD
"""
import mysql.connector
from mysql.connector import connect
import json
import os


class DBConnector:

    def __init__(self):
        self.db_user = os.getenv("MYSQL_USER")
        self.db_password = os.getenv("MYSQL_PASSWORD")

        # create firmware DB if it doesn't exist yet
        create_query = "CREATE DATABASE IF NOT EXISTS firmware;"
        try:
            with connect(user=self.db_user, password=self.db_password, host='127.0.0.1') as con:
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
          'user': self.db_user,
          'password': self.db_password,
          'host': '127.0.0.1',
          'database': 'firmware',
        }
        try:
            con = mysql.connector.connect(**config)
        except Exception as ex:
            print(ex)
        else:
            return con

    """Expects dict of firmware metadata and returns tuple in expected format for insertion into DB."""
    def _convert_firmware_dict_to_tuple(self, fw_dict):
        return (fw_dict["manufacturer"],
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
                json.dumps(fw_dict["additional_data"])
                )

    def create_table(self, table:str):
        """creates table with given table name in DB Schema

        Args:
            table (str): table name as string for table to create
        """        
        create_table_query = f"""CREATE TABLE IF NOT EXISTS {table}(
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
                cursor.execute(create_table_query)
                con.commit()
        except Exception as ex:
            print(ex)
        finally:
            con.close()

    # debugging method
    def _execute_string(self, query: str):
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

    def compare_products(self, manufacturer:str) -> list[dict]:
        """
        Compares the given product catalog in DB with the products in the products table (historized) DB.
        arguments"""
        con = self._get_db_con()

        query = f"""select * 
                    from {manufacturer} tmp, products p
                    where tmp.manufacturer = p.manufacturer
                    AND tmp.product_name = p.product_name
                    AND tmp.product_type = p.product_type
                    AND tmp.version = p.version
                    AND tmp.download_link = p.download_link
                    AND tmp.file_path = p.file_path
                    #AND tmp.checksum_local = p.checksum_local
                    AND tmp.checksum_scraped = p.checksum_scraped
                    AND tmp.emba_tested = p.emba_tested
                    AND tmp.emba_report_path = p.emba_report_path
                    AND tmp.embark_report_link = p.embark_report_link
                    AND tmp.additional_data = p.additional_data"""
        try:
            with con.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                print(result)
        except Exception as ex:
            print(ex)
        finally:
            con.close()
        return result

    def insert_products(self, product_list: list[dict], table:str="products"):
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
            (manufacturer, product_name, product_type, version, release_date, download_link, file_path, checksum_local,
             checksum_scraped, emba_tested, emba_report_path, embark_report_link, additional_data)
            VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        product_list = [self._convert_firmware_dict_to_tuple(fw_dict) for fw_dict in product_list]
        con = self._get_db_con()
        try:
            with con.cursor() as cursor:
                cursor.executemany(insert_products_query, product_list)
                con.commit()
        except Exception as ex:
            print(ex)
        finally:
            con.close()

    
    def retrieve_download_links(self):
        """Returns all download links from the firmware table.

        Returns:
            result: _description_
        """       
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

    
    def get_products(self, manufacturer='', table='products'):
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
            print(retrieve_products_query) # debug
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

    with open("../test/files/firmware_data_schneider.json", 'r') as file:
        test_data = json.loads(file.read())

    db.insert_products(test_data)

    print(*db.retrieve_download_links()[:5], sep="\n")


