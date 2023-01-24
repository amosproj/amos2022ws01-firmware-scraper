use firmware;

CREATE DATABASE IF NOT EXISTS firmware;

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