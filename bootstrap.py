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
import os
import sys

files = ['README.md', 'README.txt']
folders = ['data', 'examples']


def delFolder(path):
	if os.path.exists(path):
		for i in os.listdir(path):
			if os.path.isdir(os.path.join(path, i)):
				delFolder(os.path.join(path, i))
				os.rmdir(os.path.join(path, i))
			else:
				os.remove(os.path.join(path, i))

os.chdir('micropi')

delFolder('buildEnv/build')

data = []
for i in folders:
	datafiles = [(d, [os.path.join(d,f) for f in files])
		for d, fdrs, files in os.walk(i)]
	data += datafiles
os.chdir('..')
dd = []
for i in data:
	dd += i[1]
dd += files

argv = []
for i in sys.argv:
	if i == 'prepSetup.py':
		argv.append('setup.py')
	else:
		argv.append(i)

setupScript = """#!/usr/bin/env python
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
	  version='0.4.2',
	  description='A Micro:Bit IDE',
	  author='Nathan Taylor',
	  author_email='bottersnike237@gmail.com',
	  url='http://bottersnike.github.com/Micro-Pi',
	  scripts=['scripts/micro-pi', 'scripts/reset-micro-pi'],
	  packages=['micropi'],
	  package_dir={'micropi': 'micropi'},
	  package_data={'micropi': %s},
	  requires=['pygame', 'yotta', 'pygments'],
	  provides=['micropi'],
      long_description=open("README.txt").read(),
      license='GNU General Public License'
	 )
""" % str(dd)
open('setup.py', 'w').write(setupScript)
#os.system(' '.join(['python'] + argv))
