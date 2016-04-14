import os
import sys

files = ['config.conf']
folders = ['data', 'examples', 'buildEnv']


def delFolder(path):
	if os.path.exists(path):
		for i in os.listdir(path):
			if os.path.isdir(os.path.join(path, i)):
				delFolder(os.path.join(path, i))
				os.rmdir(os.path.join(path, i))
			else:
				os.remove(os.path.join(path, i))

os.chdir('micropi')
#for i in os.listdir('logs'):
	#if not os.path.isdir('logs/%s' % i):
		#os.remove('logs/%s' % i)

delFolder('buildEnv/build')

#open('config.conf', 'w').write("""darkHighlight: (50 , 130, 50 ),
#quickstart: False
#mbitLocation: "/media/MICROBIT"
#lightbgColour: (36, 36, 36)
#theme: "darkgreen"
#highlightColour: (73 , 182, 73 )
#backgroundColour: (36, 36, 36)
#""")

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

#open('files.txt', 'w').write('\n'.join(dd))

argv = []
for i in sys.argv:
	if i == 'prepSetup.py':
		argv.append('setup.py')
	else:
		argv.append(i)

setupScript = """
#!/usr/bin/env python

from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES

for scheme in INSTALL_SCHEMES.values():
	scheme['data'] = scheme['purelib']

setup(name='MicroPi',
	  version='0.2',
	  description='A Micro:Bit IDE',
	  author='Nathan Taylor',
	  author_email='bottersnike237@gmail.com',
	  url='http://github.com',
	  scripts=['micro-pi'],
	  long_description=\"\"\"Micro:Pi is an IDE written in pure python for
programming the BBC Micro:Bit using C++. It is designed to run on a
Raspberry Pi (hence the name) but should run on any os that has pygame
installed.

Micro:Pi is not affiliated with the BBC in any way.\"\"\",
	  packages=['micropi'],
	  package_dir={'micropi': 'micropi'},
	  package_data={'micropi': %s},
	  requires=['pygame', 'yotta'],
	  provides=['micropi']
	 )
""" % str(dd)
open('setup.py', 'w').write(setupScript)
os.system(' '.join(['python'] + argv))
