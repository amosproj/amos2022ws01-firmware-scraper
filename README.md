# Firmware Scraper (AMOS SS 2022)
[![Pytest Suite](https://github.com/amosproj/amos2022ws01-firmware-scraper/actions/workflows/pytest.yml/badge.svg)](https://github.com/amosproj/amos2022ws01-firmware-scraper/actions/workflows/pytest.yml)
![Logo of the project](https://github.com/amosproj/amos2022ws01-firmware-scraper/blob/main/Deliverables/sprint-01/team-logo-black.png?raw=true)

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

python -m src.core
```


## Links

[Feature Board](https://github.com/orgs/amosproj/projects/4)

[Impediments Backlog](https://github.com/orgs/amosproj/projects/3/views/1)

[Tasks without Feature](https://github.com/users/Deepakraj8055/projects/6)

