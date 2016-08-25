#Installing
There are two ways of installing Micro:Pi. You can either use the automated
installer (Linux only) or you can install it manually.
##Using the automated installer
If you want to use the automated installer, there are two options. You
can download just the `install.sh` file and then run the following:
```
sudo ./install.sh --online
```
This will download the rest of the files and then install them. Your other
option is to download all of the files (`git clone https://github.com/Bottersnike/Micro-Pi`)
and then just run `sudo ./install.sh`. Micro:Pi can now be run using the
command `micropi` and the serial monitor can be started with the command
`micropi-serial`.
##Installing manually
Installing manually is a bit more of a hastle, but still isn't too bad.
###Dependancys
The first step is to download all of the things required for Micro:Pi to
run. They are as follows:
- python 2.7 [https://www.python.org/.../python-2.7.12.msi](https://www.python.org/ftp/python/2.7.12/python-2.7.12.msi)
- pyGTK2.0 All In One[http://ftp.gnome.org/.../pygtk-all-in-one-2.24.2.win32-py2.7.msi](http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/2.24/pygtk-all-in-one-2.24.2.win32-py2.7.msi)
    (Be sure to check PyGtkSourceView2 2.10.1 in the installation window)
- yotta [https://mbed-media.mbed.com/.../yotta_install_v023.exe](https://mbed-media.mbed.com/filer_public/2f/0b/2f0b924c-1fac-4907-989b-f2afe3f5785e/yotta_install_v023.exe)
- gcc-arm-none-eabi [https://launchpad.net/.../gcc-arm-none-eabi-4_9-2015q2-20150609-win32.exe](https://launchpad.net/gcc-arm-embedded/4.9/4.9-2015-q2-update/+download/gcc-arm-none-eabi-4_9-2015q2-20150609-win32.exe)

Now you need to add the location where you installed yotta (C:\yotta by
default) and the \bin directory of you gcc-arm-none-eabi installation to
your global path. Instructions for adding to you path can be found at
[http://yottadocs.mbed.com/#windows-path](http://yottadocs.mbed.com/#windows-path).
If you want you can also remove the "Run Yotta" shortcut from your
desktop as you don't need it.
####Installing
Now open a terminal in the same folder as `README.md` and `setup.py` and
run `python setup.py install`. This will install Micro:Pi and you are
now able to start Micro:Pi from the terminal with the command `micropi`
and you can start the serial monitor with `micropi-serial`.
