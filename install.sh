#!/bin/bash

if [ "$(id -u)" != "0" ]; then
    echo -e "\033[31m====================================="
    echo -e "=  This script must be run as root. ="
    echo -e "=  Please run this script again on  ="
    echo -e "=     an account with significant   ="
    echo -e "= privilages (sudo bash install.sh) ="
    echo -e "=====================================\033[37m"
    exit 1
fi

echo -e "\033[32m======================================"
echo "= Welcome to the Micro:Pi installer! ="
echo "=   We're going to run you through   ="
echo "=  installing Micro:Pi so that you   ="
echo "=   can just sit back and watch it   ="
echo "=               install              ="
echo -e "======================================\033[37m"

echo "Installing Required Porgrams:"
if apt-get update && sudo apt-get install srecord python python-pip cmake gcc-arm-none-eabi python-setuptools build-essential ninja-build python-dev libffi-dev; then
    echo "Dependancys Fetched"
else
    echo -e "\033[31m==================================="
    echo "=  There was an error installing  ="
    echo "=          dependencies           ="
    echo -e "===================================\033[37m"
    exit 1
fi
echo "Installing Yotta:"
if pip install yotta; then
    echo "Dependencies Fetched"
else
    echo -e "\033[31m==================================="
    echo "=  There was an error installing  ="
    echo "=              yotta              ="
    echo -e "===================================\033[37m"
    exit 1
fi
echo "Fetching Micro:Pi"

cp -vr micropi/ /usr/local/lib/python2.7/dist-packages/micropi/
cd scripts
chmod +x *
cp -v micropi /usr/bin/
cp -v reset-micropi /usr/bin/
chmod +x /usr/bin/micropi
chmod +x /usr/bin/reset-micropi
