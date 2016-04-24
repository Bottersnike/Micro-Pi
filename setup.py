#!/usr/bin/env python
#  micropi.py
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
from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES

for scheme in INSTALL_SCHEMES.values():
	scheme['data'] = scheme['purelib']

setup(name='MicroPi',
	  version='0.3.9',
	  description='A Micro:Bit IDE',
	  author='Nathan Taylor',
	  author_email='bottersnike237@gmail.com',
	  url='http://bottersnike.github.com/Micro-Pi',
	  scripts=['scripts/micro-pi', 'scripts/reset-micro-pi'],
	  packages=['micropi'],
	  package_dir={'micropi': 'micropi'},
	  package_data={'micropi': ['data/Monospace.ttf', 'data/Roboto-Light.ttf', 'data/icon.png', 'data/Roboto.ttf', 'data/icons/buildRed.png', 'data/icons/uploadGreen.png', 'data/icons/menuBlue.png', 'data/icons/buildYellow.png', 'data/icons/uploadYellow.png', 'data/icons/consoleYellow.png', 'data/icons/consoleGreen.png', 'data/icons/menuYellow.png', 'data/icons/uploadBlue.png', 'data/icons/consoleBlue.png', 'data/icons/consoleRed.png', 'data/icons/menuGreen.png', 'data/icons/buildGreen.png', 'data/icons/buildBlue.png', 'data/icons/uploading.png', 'data/icons/uploadRed.png', 'data/icons/menuRed.png', 'data/icons/building.png', 'data/icons/SVG/uploadRed.svg', 'data/icons/SVG/uploading.svg', 'data/icons/SVG/buildBlue.svg', 'data/icons/SVG/ico.svg', 'data/icons/SVG/buildRed.svg', 'data/icons/SVG/uploadGreen.svg', 'data/icons/SVG/uploadYellow.svg', 'data/icons/SVG/uploadBlue.svg', 'data/icons/SVG/buildGreen.svg', 'data/icons/SVG/buildYellow.svg', 'data/icons/SVG/building.svg', 'data/splashScreens/1.png', 'examples/Button.mpi', 'examples/Scroll.mpi', 'Button.mpi', 'Scroll.mpi']},
	  requires=['pygame', 'yotta'],
	  provides=['micropi'],
      long_description=open("README.txt").read(),
      license='GNU General Public License'
	 )
