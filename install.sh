#!/bin/bash

echo "Checking system requirements"

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
    echo "Warning: This program is only optimized for use under Ubuntu 22.04!"
fi

echo "Setting up virtual environment"
python -m venv .venv
source .venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup complete!"
