#!/usr/bin/env python
#  setup.py
#
#  Copyright 2016  Nathan Taylor
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
from setuptools import setup
import os

print "Warning!"
print "This script will NOT install pygtk or gtksourceview2!"
print "To install them on windows download and install",
print "http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/2.24/pygtk-all-in-one-2.24.2.win32-py2.7.msi"
print "If you are on linux you should use the install.sh file instead",
print "of this one."
raw_input("I have read the above and am ready to continue installation (HIT RETURN)")

os.chdir("micropi")
d  = [os.path.join(dp, f) for dp, dn, fn in os.walk("data") for f in fn]
d += [os.path.join(dp, f) for dp, dn, fn in os.walk("examples") for f in fn]
d += [os.path.join(dp, f) for dp, dn, fn in os.walk("docs") for f in fn]
os.chdir("..")

setup(name="MicroPi",
      version="0.9.7",
      description="A BBC Micro:Bit IDE",
      author="Nathan Taylor",
      author_email="bottersnike237@gmail.com",
      url="http://bottersnike.github.co/Micro-Pi",
      scripts=["scripts/micropi", "scripts/micropi-serial"],
      packages=["micropi"],
      package_dir={"micropi": "micropi"},
      package_data={"micropi": d},
      install_requires=[],
      provides=["micropi"],
      long_description=open("README.md").read(),
      license="GNU General Public License"
     )
