#!/bin/bash

if [ "$(id -u)" != "0" ]; then
    echo -e "\033[31m======================================="
    echo -e "=   This script must be run as root.  ="
    echo -e "=   Please run this script again on   ="
    echo -e "=      an account with significant    ="
    echo -e "= privilages (sudo bash uninstall.sh) ="
    echo -e "=======================================\033[37m"
    exit 1
fi

echo -e "\033[32m========================================"
echo "= Welcome to the Micro:Pi uninstaller! ="
echo "=   We're going to run you through     ="
echo "=  uninstalling Micro:Pi so that you   ="
echo "=   can just sit back and watch it     ="
echo "=              uninstall               ="
echo -e "========================================\033[37m"

echo "Removing Scripts:"

rm -v /usr/bin/micropi
rm -v /usr/bin/reset-micropi

echo "Removing Data:"

rm -rv $(eval echo ~$(logname)/.micropi)

echo "Removing Micro:Pi:"

rm -rv /usr/local/lib/python2.7/dist-packages/micropi/

echo -e "\033[32m================================"
echo "= We're sorry to see you go :( ="
echo -e "================================\033[37m"
