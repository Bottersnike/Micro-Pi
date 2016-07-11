#!/bin/sh
#  uninstall.sh
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

if [ "$(id -u)" != "0" ]; then
    echo "\033[31m======================================="
    echo "=  This script must be run as root. ="
    echo "=  Please run this script again on  ="
    echo "=     an account with significant   ="
    echo "= privilages (sudo sh uninstall.sh) ="
    echo "=======================================\033[37m"
    exit 1
fi

echo "\033[32m========================================"
echo "= Welcome to the Micro:Pi uninstaller! ="
echo "=   We're going to run you through     ="
echo "=  uninstalling Micro:Pi so that you   ="
echo "=   can just sit back and watch it     ="
echo "=              uninstall               ="
echo "========================================\033[37m"

echo "Removing Scripts:"

rm -v /usr/bin/micropi
rm -v /usr/bin/micropi-serial

echo "Removing Data:"

rm -rv $(eval echo ~$(logname)/.micropi)

echo "Removing Micro:Pi:"

rm -rv /usr/local/lib/python2.7/dist-packages/micropi/

echo "\033[32m================================"
echo "= We're sorry to see you go :( ="
echo "================================\033[37m"
