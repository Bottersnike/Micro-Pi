#!/bin/sh
#  install.sh
#
#  Copyright 2016 Nathan Taylor
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

installdeps=1
online=0
help=0

while [ "$1" != "" ]; do
    case $1 in
        -o | --online    )        online=1
                                  ;;
        -n | --nodeps    )        installdeps=0
                                  ;;
        -h | --help )        help=1
                                  ;;
    esac
    shift
done

if [ $help -eq 1 ]; then
    echo "Help:"
    echo ""
    echo "-o --online         Online install"
    echo "-n --nodeps         Install without collecting dependancys"
    echo "-h --help        Show this help message"
    exit 0
fi

if [ "$(id -u)" != "0" ]; then
    echo "\033[31m====================================="
    echo "=  This script must be run as root. ="
    echo "=  Please run this script again on  ="
    echo "=     an account with significant   ="
    echo "=  privilages (sudo sh install.sh)  ="
    echo "=====================================\033[37m"
    exit 1
fi

echo "\033[32m======================================"
echo "= Welcome to the Micro:Pi installer! ="
echo "=   We're going to run you through   ="
echo "=  installing Micro:Pi so that you   ="
echo "=   can just sit back and watch it   ="
echo "=               install              ="
echo "======================================\033[37m"

if [ $installdeps -eq 1 ]; then
    echo "Installing Required Porgrams:"
    if apt-get update && sudo apt-get install srecord python python-pip cmake gcc-arm-none-eabi python-setuptools build-essential ninja-build python-dev libffi-dev libssl-dev; then
        echo "Dependancys Fetched"
    else
        echo "\033[31m==================================="
        echo "=  There was an error installing  ="
        echo "=          dependencies           ="
        echo "===================================\033[37m"
        exit 1
    fi

    echo "Installing Yotta:"
    if pip install yotta; then
        echo "Dependencies Fetched"
    else
        echo "\033[31m==================================="
        echo "=  There was an error installing  ="
        echo "=              yotta              ="
        echo "===================================\033[37m"
        exit 1
    fi
else
    echo "Skipping Dependancys"
fi

if [ $online -eq 1 ]; then
    echo "Fetching Micro:Pi"
    git clone https://github.com/Bottersnike/Micro-Pi.git MicroPi
    cd MicroPi

    cp -rv micropi/ /usr/local/lib/python2.7/dist-packages/micropi/
    cd scripts
    chmod +x *
    cp -v micropi /usr/bin/
    chmod +x /usr/bin/micropi
    cd ..
    cp uninstall.sh ..

    cd ..
    rm -rf MicroPi
else
    echo "Using Offline Download"
    cp -rv micropi/ /usr/local/lib/python2.7/dist-packages/micropi/
    cd scripts
    chmod +x *
    cp -v micropi /usr/bin/
    cp -v micropi-serial /usr/bin/
    chmod +x /usr/bin/micropi
fi
