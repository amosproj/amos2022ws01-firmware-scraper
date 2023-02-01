#!/bin/bash

## Color definition
export RED="\033[0;31m"
export GREEN="\033[0;32m"
export ORANGE="\033[0;33m"
export MAGENTA="\033[0;35m"
export CYAN="\033[0;36m"
export BLUE="\033[0;34m"
export NC="\033[0m"  # no color

## Attribute definition
export BOLD="\033[1m"

echo -e "\\n""$GREEN""$BOLD""AMOS Firmware Scraper""$NC"

echo -e "$NC""Checking system requirements..."

SUB="Ubuntu 22.04"
DISTRO=""

if [[ "$OSTYPE" == "linux-gnu" ]]
then
    if command -v lsb_release &> /dev/null
    then
        DISTRO=$(lsb_release -d | awk -F"\t" '{print $2}')
        if [[ $DISTRO == *$SUB* ]]
        then :
        fi
    fi
else
    echo -e "$RED""$BOLD""WARNING: This program is only optimized for use under Ubuntu 22.04!\n"
    read -p "Do you want to continue the installation anyway? (y/n) " yn
    case $yn in 
        [yY] ) echo ;;
        [nN] ) echo "exiting...";
            exit;;
        * ) echo "invalid response";;
    esac
fi

# Check if git exists and install if not
echo -e "$NC""Installing necessary packages..."
if ! command -v git > /dev/null ; then
apt-get install -y git
fi

# Check if python exists and install if not
if ! command -v python3.10 > /dev/null ; then
apt-get install -y python3.10
fi
if ! command -v python-is-python3 > /dev/null ; then
apt-get install -y python-is-python3
fi
if ! command -v pip3.10 > /dev/null ; then
apt-get install -y python3-pip
fi
if ! command -v python3.10-venv > /dev/null ; then
apt-get install -y python3.10-venv
fi

# Check if mysql exists and install if not
if ! command -v mysql > /dev/null ; then
apt-get install -y mysql-server
fi

# Clone git repository
echo -e "$NC""Cloning code repository..."
git clone https://github.com/amosproj/amos2022ws01-firmware-scraper.git
cd amos2022ws01-firmware-scraper

echo -e "$NC""Setting up virtual environment..."
python -m venv .venv
source .venv/bin/activate

echo -e "$NC""Installing dependencies..."
pip install -r src/requirements.txt

echo -e "$NC""Setup complete!"
