# Firmware Scraper (AMOS SS 2022)
[![Pytest Suite](https://github.com/amosproj/amos2022ws01-firmware-scraper/actions/workflows/pytest.yml/badge.svg)](https://github.com/amosproj/amos2022ws01-firmware-scraper/actions/workflows/pytest.yml)
![Logo of the project](https://github.com/amosproj/amos2022ws01-firmware-scraper/blob/main/Deliverables/sprint-01/team-logo-white.png?raw=true)

## TLDR;

This [Selenium-based](https://github.com/SeleniumHQ/selenium) firmware scraper gathers firmware data from 25 vendors. Our automated solution scrapes meta data from numerous vendors and downloads corresponding firmwares. The results can be used for InfoSec research.

## Installation
```shell
git clone https://github.com/amosproj/amos2022ws01-firmware-scraper
# or download and unpack .zip amos2022ws01-firmware-scraper-main
cd amos2022ws01-firmware-scraper
./install.sh

# Make sure MySQL server is running
# On macOS
sudo launchctl load -F /Library/LaunchDaemons/com.oracle.oss.mysql.mysqld.plist
# On Linux
/etc/init.d/mysqld start

export MYSQL_USER=<your username>
export MYSQL_PASSWORD=<your password>

python -m src.core![image](https://user-images.githubusercontent.com/18518249/214767799-4d9e53a5-bf8b-4cff-b44c-77bebb41418e.png)

```
**Requirements**: Git and Python 3.10 must be installed on your machine.

The preferred way to run the application is to use Docker Compose. This option lets you quickly and seamlessly start the application using a single command.


```shell
git clone https://github.com/amosproj/amos2022ws01-firmware-scraper
#or download and unpack .zip mos2022ws01-firmware-scraper-main
cd amos2022ws01-firmware-scraper
python3 -m venv .AMOS
source .AMOS/bin/activate
pip install -r requirements.txt

# Make sure MySQL server is running
# On macOS
sudo launchctl load -F /Library/LaunchDaemons/com.oracle.oss.mysql.mysqld.plist
# On Linux
/etc/init.d/mysqld start

export MYSQL_USER=<your username>
export MYSQL_PASSWORD=<your password>

cd src
python3 -m src.core
```

## Option: Docker 
```shell
git clone https://github.com/amosproj/amos2022ws01-firmware-scraper
#or download and unpack .zip mos2022ws01-firmware-scraper-main
cd amos2022ws01-firmware-scraper
docker-compose up --build
```
**Requirements**: docker should be installed on your machine.
