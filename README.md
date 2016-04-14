##Summary
Micro:Pi is a pure python IDE (Intergrated
Development Enviroment) designed to run on any system
with python. It has a simple interface and features
including built in examples, file inporting, and even
different themes to suit how you are feeling.

##Why use Micro:Pi over alternatives?
For starters, once you have donloaded the yotta
build setup (included with the pip package) it's
entirely offline and doens't require any internet
connection at all. Seccondly, it is an IDE for C++. C++
if the langauge that all of the other editors are build
arround, but none of them atchually allow you to
program in it. All except for Micro:Pi! Other than that
it is self contained, simple to use, contains lots of
little features to speed up your day. And, oh! Did I
mention that it's open source?

##Instalation
On a raspberry pi (the intended platform) it's
simple. Open up a terminal and type the following:
    sudo apt-get install srecord cmake ninja-build
    sudo pip install micropi
Then to start it simple type `sudo micro-pi`
into a terminal window.
On other platforms, you may need
to download and install cmake, ninja-build and
srecord manually, but Micro:Pi can still be installed
with pip. On Windows (also posiably mac) you need to
run `python -m micropi` to start it. If pip is
unavaliable, you can download the .zip file from
the [PyPi Warehouse](http://warehouse.python.org/project/MicroPi), extract
it, then run `python setup.py install`

##Features
- In the top left corner are 4 triangles that indicate the statud of you
    Micro:Bit. You highligh colour to say it's plugged in. Orange if
    it's uploading, and red is if Micro:Pi can't find you Micro:Bit.
- Just underneath the 4 triangles, is your tab view. This allows you to
    create multiple files in your project.
- On the far right are 4 icons. From left to right they are, build,
    build and upload, toggle console and menu.
- The menu can be shown by clicking the menu icon and in it you have the
    option to do things like save, load and quit, but there are also
    some things like "import file" which allows you to add a file to
    your workspace and "reset build" which resets the enviroment in
    which Micro:Pi creates your finished code.
- If you hover over "Examples" a submenu appears from which you can
    chose pre-made examples to help you get started.
- If you click on settings from the menu, you will be greeted with the
    screen show in the screen shot and the options are as follows:
  - Quick Start:  This toggles whether to reset the build enviroment every time you start Micro:Pi. It is reccomended to put this on and just use "Rest Build" from the menu if you need to.
  - Micro:Bit Location:  This is where Micro:Pi tries to find your Micro:Bit. On windows change it to something like "E:\" or whatevery your Micro:Bit's drive letter is. (Use the arrow keys to move the cursor)
  - Theme:  Use the round buttons to select your chosen theme.
* The large white box in the top half of the screen is your text editor.
    This is where you write your code to put on your Micro:Bit
* Just under that, if you have the console toggled on, is the console.
    Here you will see status on how your build is doing and any errors
    in your code.

##Contribute
If you want to contribute, then at the moment there isn't
a paypal button or anything like that, but if you are any
good at art then you could contribute by creating some new
buttons for the top right. At the moment, they are a bit
rubish and are only really placeholders. Also you could
create some more splash screens as veriety is cool. This
website could also do with some work if someone is willing
to put in the time. In fact, if you really wanted you could
help with the code because things like dragging to select
text, copy/paste, Xscroll aren't yet implemented. You can
find the source code either at [http://github.com/Bottersnike/MicroPi](http://github.com/Bottersnike/Micro-Pi)
or by downloading the zip from [http://warehouse.python.org/project/MicroPi](http://warehouse.python.org/project/MicroPi). If you
have created something, you can email it to me at
[bottersnike237@gmail.com](mailto:bottersnike237@gmail.com)

##Thanks To:
- The MBED team for developing yotta and alot of the build process
- Lancaster University for the microbit-dal runtime that this entire project is built upon
- Joe Finney from Lancaster Uni. for helping me when I was facing problems settings up yotta on my pi
- The entire Raspberry Pi Forums community for answering all my questions
