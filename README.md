# Firmware Scraper (AMOS SS 2022)
[![Pytest Suite](https://github.com/amosproj/amos2022ws01-firmware-scraper/actions/workflows/pytest.yml/badge.svg)](https://github.com/amosproj/amos2022ws01-firmware-scraper/actions/workflows/pytest.yml)
![Logo of the project](https://github.com/amosproj/amos2022ws01-firmware-scraper/blob/main/Deliverables/sprint-01/team-logo-white.png?raw=true)

## TLDR;

This [Selenium-based](https://github.com/SeleniumHQ/selenium) firmware scraper gathers firmware data from 25 vendors. Our automated solution scrapes meta data from numerous vendors and downloads corresponding firmwares. The results can be used for InfoSec research.

## Installation
## Option 1: On your local machine

```shell
git clone https://github.com/amosproj/amos2022ws01-firmware-scraper
# or download and unpack .zip amos2022ws01-firmware-scraper-main
cd amos2022ws01-firmware-scraper
sudo ./install.sh

# Make sure MySQL server is running
# On macOS
sudo launchctl load -F /Library/LaunchDaemons/com.oracle.oss.mysql.mysqld.plist
# On Linux
/etc/init.d/mysqld start

export MYSQL_USER=<your username>
export MYSQL_PASSWORD=<your password>
export LOG_LEVEL=DEBUG

cd src
python3 -m src.core
```

## Option 2: Docker 
**Requirements**: Docker should be installed on your machine.

```shell
git clone https://github.com/amosproj/amos2022ws01-firmware-scraper
#or download and unpack .zip mos2022ws01-firmware-scraper-main
cd amos2022ws01-firmware-scraper
docker-compose up --build
```

