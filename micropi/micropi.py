#  micropi.py
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
import gobject
gobject.threads_init()
import pygtk
pygtk.require('2.0')
import gtk
import pango
import pickle
from threading import Thread
import time
import os
from subprocess import PIPE, Popen
from gtksourceview2 import View as SourceView
import gtksourceview2 as gtkSourceView
from Queue import Queue, Empty
import tempfile
import base64
import buildenv
import tarfile
import platform
import webbrowser
import serial
import serial.tools.list_ports as list_ports
import string
import random
import struct

def printError():
    data = ''
    try:
        d = ['architecture',
             'dist',
             'machine',
             'platform',
             'python_build',
             'python_compiler',
             'python_version',
             'release',
             'system',
             'version',
            ]
        for i in d:
            exec('a=platform.%s()'%i)
            data += str(i) + ' ' +  str(a) + '\n'
        data += '\ngtk ' + str(gtk.ver)
        data += '\nplatform' + str(platform.__version__)
        data += '\ntarfile' + str(tarfile.__version__)
        data += '\npango' + str(pango.version())
        data += '\nglib' + str(gobject.glib_version)
        data += '\npygobject' + str(gobject.pygobject_version)
        data += '\npickle' + str(pickle.__version__)

    except Exception as e:
        print e
    finally:
        print data

#printError()

class EntryDialog(gtk.MessageDialog):
    def __init__(self, *args, **kwargs):
        if 'default_value' in kwargs:
            default_value = kwargs['default_value']
            del kwargs['default_value']
        else:
            default_value = ''
        super(EntryDialog, self).__init__(*args, **kwargs)
        entry = gtk.Entry()
        entry.set_text(str(default_value))
        entry.connect("activate",
                      lambda ent, dlg, resp: dlg.response(resp),
                      self, gtk.RESPONSE_OK)
        self.vbox.pack_end(entry, True, True, 0)
        self.vbox.show_all()
        self.entry = entry

    def set_value(self, text):
        self.entry.set_text(text)

    def run(self):
        result = super(EntryDialog, self).run()
        if result == gtk.RESPONSE_OK:
            text = self.entry.get_text()
        else:
            text = None
        return text

def message(message, parent=None):
    dia = gtk.MessageDialog(parent, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, message)
    dia.show()
    dia.run()
    dia.destroy()
    return False

def ask(query, parent=None):
    dia = gtk.MessageDialog(parent, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, query)
    dia.show()
    rtn=dia.run()
    dia.destroy()
    return rtn == gtk.RESPONSE_YES

def askQ(query, prompt=None, parent=None):
    if prompt:
        dia = EntryDialog(parent, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, query, default_value=prompt)
    else:
        dia = EntryDialog(parent, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, query)
    dia.show()
    rtn=dia.run()
    dia.destroy()
    return rtn

def uBitPoller(self):
    last = (False, False)
    while True:
        self.uBitFound = os.path.exists(SETTINGS['mbitLocation'])
        if not (self.uBitUploading and self.uBitFound):
            if self.uBitFound and not last[0]:
                gobject.idle_add(self.indicator.set_from_file, "data/uBitFound.png")
            elif last[0] and not self.uBitFound:
                gobject.idle_add(self.indicator.set_from_file, "data/uBitNotFound.png")
                self.uBitUploading = False
        else:
            gobject.idle_add(self.indicator.set_from_file, "data/uBitUploading.png")
        time.sleep(0.2)
        last = (self.uBitFound, self.uBitUploading)

def pipePoller(self):
    def addText(self, text):
#        pass
        tb = self.consoleBody.get_buffer()
        tb.insert(tb.get_end_iter(), text)
    while True:
        if self.pipes:
            try:
                d1 = self.pipes[1].readline()
                d2 = self.pipes[2].readline()
            except UnexpectedEndOfStream:
                pass

            if type(d1) != str:
                d1 = str(d1, encoding="utf-8")
            if type(d2) != str:
                d2 = str(d2, encoding="utf-8")

            tb = self.consoleBody.get_buffer()
            tb.insert(tb.get_end_iter(), d1 + d2)
            #gobject.idle_add(addText, self, d1 + d2)

            if not (self.pipes[1].alive() or self.pipes[2].alive()):
                self.pipes = None
                self.mbedBuilding = False
                os.chdir(self.prevLoc)
                if os.path.exists('%s/build/bbc-microbit-classic-gcc/source/microbit-combined.hex' % buildLocation):
                    tb = self.consoleBody.get_buffer()
                    tb.insert(tb.get_end_iter(), "Done!\n")
                    #gobject.idle_add(addText, self, "Done!\n")
                    if self.mbedUploading and self.uBitFound:
                        gobject.idle_add(addText, self, "Uploading!\n")
                        tb = self.consoleBody.get_buffer()
                        tb.insert(tb.get_end_iter(), "Uploading!\n")
                        #self.uBitUploading = True
                        thread = Thread(target=upload, args=(self,))
                        thread.daemon = True
                        thread.start()
                    elif self.mbedUploading:
                        self.uBitUploading = False
                        self.mbedUploading = False
                        gobject.idle_add(self.message, """Cannot upload!
Micro:Bit not found!
Check it is plugged in and
Micro:Pi knows where to find it.""")
                else:
                    gobject.idle_add(self.message, """There is an error
with your code!
It is advised to scroll
back through the console
to find out what the error is!""")
                    self.uBitUploading = False
                    self.mbedUploading = False
        else:
            time.sleep(0.1)

def upload(self):
    end = open('%s/build/bbc-microbit-classic-gcc/source/microbit-combined.hex' % buildLocation).read()
    open(
        '%s/microbit-combined.hex' % SETTINGS['mbitLocation'],
        'w'
    ).write(end)
    self.mbedUploading = False

def updateTitle(self):
    lastTitle = ''
    while True:
        start = '*' if self.getModified() else ''
        fn = os.path.basename(self.saveLocation)
        full = os.path.dirname(self.saveLocation)
        end = 'Micro:Pi'

        title = '%s%s - %s - %s' % (start, fn, full, end)

        if title != lastTitle:
            self.window.set_title(title)

        lastTitle = title

        time.sleep(0.1)

def serialPoller(self):
    start = True
    def addText(self, text):
        tb = self.consoleBody.get_buffer()
        tb.insert(tb.get_end_iter(), text)
    while True:
        if self.serialConnection:
            try:
                data = self.serialConnection.read()
                d2 = ''
                for i in data:
                    if i in string.printable:
                        d2 += i
                gobject.idle_add(addText, self, d2)
            except:
                pass
        else:
            try:
                self.serialConnection = serial.serial_for_url(self.serialLocation)
                self.serialConnection.baudrate = self.baudrate
            except:
                pass
            time.sleep(0.1)

def saveSettings():
    data = ''
    for i in SETTINGS.keys():
        p2 = str(SETTINGS[i])
        if type(SETTINGS[i]) == str or type(SETTINGS[i]) == type(u''):
            p2 = '"%s"' % p2
        data += '%s: %s\n' % (str(i), p2)
    open(configLocation, 'w').write(data)

class NBSR:
    """
    A wrapper arround PIPES to make them easier to use
    """

    def __init__(self, stream, parent):
        self._s = stream
        self._q = Queue()
        self._a = True
        self.__a = True
        self._p = parent

        def _populateQueue(stream, queue):
            while self.__a:
                line = stream.readline()
                if type(line) == str:
                    queue.put(line)
        def _killWhenDone(parent):
            parent.wait()
            self.__a = False
            data = self._s.read()
            self._q.put(data)
            while not self._q.empty():
                pass
            self._a = False

        self._t = Thread(
            target=_populateQueue,
            args=(self._s, self._q)
        )
        self._t.daemon = True
        self._t.start()

        self._t2 = Thread(
            target=_killWhenDone,
            args=(self._p,)
        )
        self._t2.daemon = True
        self._t2.start()

    def readline(self, timeout=None):
        try:
            return self._q.get(
                block=timeout is not None,
                timeout=timeout
            )
        except Empty:
            return ''

    def alive(self):
        return self._a

class UnexpectedEndOfStream(BaseException):
    pass

class MainWin:
    def __init__(self, fileData=None):
        mgr = gtkSourceView.style_scheme_manager_get_default()
        self.style_scheme = mgr.get_scheme('oblivion')
        self.language_manager = gtkSourceView.language_manager_get_default()
        self.language = self.language_manager.get_language('cpp')

        self.window = gtk.Window()
        self.fullscreenToggler = FullscreenToggler(self.window)
        self.window.connect_object('key-press-event', FullscreenToggler.toggle, self.fullscreenToggler)
        self.window.set_title('Micro:Pi')
        self.window.set_icon_from_file('data/icon.png')
        self.window.resize(750, 500)
        colour = gtk.gdk.color_parse('#242424')
        self.window.modify_bg(gtk.STATE_NORMAL, colour)

        self.window.connect("delete_event", self.destroy)

        self.serialConsole = SerialConsole()

        self.table = gtk.Table(5, 1, False)
        self.table.show()
        self.window.add(self.table)

        self.uBitUploading = False
        self.mbedBuilding = False
        self.mbedUploading = False
        self.uBitFound = False

        self.tabWidth = 4
        self.autoIndent = True
        self.lineNumbers = True

        self.saveLocation = ''

        exampleMenu = [(i[:-(len(SETTINGS['fileExtention'])+1)] if i[-(len(SETTINGS['fileExtention'])+1):] == '.'+SETTINGS['fileExtention'] else i, (self.loadExample, '', '', i))
                   for i in os.listdir('examples')]
        menuData = [
                    ("_File", [
                              ("_New Project", (self.newProject, gtk.STOCK_NEW, '<Control>N')),
                              ("Add _Page", (self.newPage, gtk.STOCK_NEW, '')),
                              ("_Examples", exampleMenu),
                              ("_Import File", (self.importFile, gtk.STOCK_ADD, '<Control>I')),
                              ("_Open", (self.openFile, gtk.STOCK_OPEN, '<Control>O')),
                              ("_Save", (self.save, gtk.STOCK_SAVE, '<Control>S')),
                              ("Save _As", (self.saveAs, gtk.STOCK_SAVE_AS, '')),
                              ('', ''),
                              ("_Quit", (self.destroy, gtk.STOCK_QUIT, '<Control>Q'))
                             ]
                    ),
                    ("_Edit", [
                               ("_Undo", (self.sendUndo, gtk.STOCK_UNDO, '<Control>Z')),
                               ("_Redo", (self.sendRedo, gtk.STOCK_REDO, '<Control>Y')),
                               ('', ''),
                               ("Cu_t", (self.sendCut, gtk.STOCK_CUT, '<Control>X')),
                               ("_Copy", (self.sendCopy, gtk.STOCK_COPY, '<Control>C')),
                               ("_Paste", (self.sendPaste, gtk.STOCK_PASTE, '<Control>V')),
                               ('', ''),
                               ("Select _All", (self.sendSelectAll, gtk.STOCK_SELECT_ALL, '<Control>A')),
                               ('', ''),
                               ("Preference_s", [
                                                 ('Set Micro:Bit Location', (self.setUBitLoc, '', '')),
                                                 ("Enable _Quick Statrt", (self.toggleQS, '', '', '', 'checkbox', SETTINGS['quickstart'])),
                                                ]
                               ),
                              ]
                    ),
                    ("_View", [
                               ("Show _Line Numbers", (self.lineNumbersToggle, '', '', '', 'checkbox', True)),
                               ("Enable Auto _Indent", (self.autoIndentToggle, '', '', '', 'checkbox', True)),
                               ("_Tab Width", [
                                              ("2", (self.setTabWidth, '', '', '', 'radio', False, 'radioGroup1', 2)),
                                              ("4", (self.setTabWidth, '', '', '', 'radio', True, 'radioGroup1', 4)),
                                              ("6", (self.setTabWidth, '', '', '', 'radio', False, 'radioGroup1', 6)),
                                              ("8", (self.setTabWidth, '', '', '', 'radio', False, 'radioGroup1', 8)),
                                              ("10", (self.setTabWidth, '', '', '', 'radio', False, 'radioGroup1', 10)),
                                              ("12", (self.setTabWidth, '', '', '', 'radio', False, 'radioGroup1', 12)),
                                             ]
                               ),
                              ]
                    ),
                    ("_Deploy", [
                                ("_Build", (self.startBuild, gtk.STOCK_EXECUTE, '<Control>B')),
                                ("Build and _Upload", (self.startBuildAndUpload, '', '<Control>U')),
                                ("_Force Upload", (self.forceUpload, gtk.STOCK_DISCONNECT, '')),
                                ('', ''),
                                ("Serial _Monitor", (self.serialConsole.toggleVis, '', '<Control>M'))
                               ]
                    ),
                    ("_Help", [
                               ("_Website", (self.website, gtk.STOCK_HELP, 'F1')),
                               ("_About", (self.showAbout, gtk.STOCK_ABOUT, '')),
                              ]
                    ),
                   ]

        agr = gtk.AccelGroup()
        self.window.add_accel_group(agr)

        def loadMenu(menu, first=True):
            radioGroups = {}
            np = gtk.MenuBar() if first else gtk.Menu()
            for i in menu:
                if i == ('', ''):
                    sep = gtk.SeparatorMenuItem()
                    sep.show()
                    np.append(sep)
                elif type(i[1]) == list:
                    dt = loadMenu(i[1], False)
                    mi = gtk.MenuItem(i[0])
                    mi.show()
                    mi.set_submenu(dt)
                    np.append(mi)
                elif len(i[1]) == 3 or len(i[1]) == 4:
                    dat = i[1]
                    if dat[1]:
                        mi = gtk.ImageMenuItem(dat[1])
                        mi.get_children()[0].set_label(i[0])
                    else:
                        mi = gtk.MenuItem(i[0])
                    if dat[0]:
                        if len(dat) == 3:
                            mi.connect("activate", dat[0])
                        elif len(dat) == 4:
                            mi.connect_object("activate", dat[0], dat[3])
                    if dat[2]:
                        key, mod = gtk.accelerator_parse(dat[2])
                        mi.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)
                    mi.show()
                    np.append(mi)
                elif len(i[1]) > 4:
                    dat = i[1]
                    if dat[4] == "checkbox":
                        mi = gtk.CheckMenuItem(i[0])
                        if len(dat) == 6:
                            mi.set_active(dat[5])
                        if dat[0]:
                            mi.connect("activate", dat[0])
                        mi.show()
                        np.append(mi)
                    elif dat[4] == "radio":
                        mi = gtk.RadioMenuItem(label=i[0])
                        if dat[6] not in radioGroups:
                            radioGroups[dat[6]] = mi
                        else:
                            mi.set_group(radioGroups[dat[6]])
                        if dat[5]:
                            mi.set_active(True)
                        if dat[0]:
                            mi.connect("activate", dat[0], dat[7])
                        mi.show()
                        np.append(mi)
            return np

        self.menu = loadMenu(menuData)
        self.table.attach(self.menu, 0, 1, 0, 1, yoptions = 0)
        self.menu.show()

        tbW = gtk.VBox(False)
        self.toolbar = gtk.HBox(False)

        self.indicator = gtk.Image()
        self.indicator.set_from_file("data/uBitNotFound.png")
        self.indicator.show()
        self.toolbar.pack_start(self.indicator, False)

        self.toolbar.show()
        tbW.pack_start(self.toolbar, True, True, 0)
        tbW.show()
        self.table.attach(tbW, 0, 5, 1, 2, gtk.FILL, gtk.FILL)

        self.notebook = gtk.Notebook()
        self.table.attach(self.notebook, 0, 1, 2, 4)
        self.notebook.show()
        if not fileData:
            fileData = [('main.cpp', """#include "header.h"
#include "MicroBit.h"

void app_main()
{

}
"""), ('header.h', '')]
        for i in fileData:
            self.addNotebookPage(*i)

        self.consoleFrame = gtk.ScrolledWindow()
        self.consoleFrame.set_policy(gtk.POLICY_ALWAYS, gtk.POLICY_ALWAYS)
        self.consoleFrame.show()

        txtB = gtkSourceView.Buffer()
        txtB.set_style_scheme(self.style_scheme)
        txtB.set_highlight_matching_brackets(False)
        txtB.set_highlight_syntax(False)
        txtB.place_cursor(txtB.get_start_iter())

        self.consoleBody = SourceView(txtB)
        self.consoleBody.modify_font(pango.FontDescription('Monospace 10'))
        self.consoleBody.show()
        self.consoleFrame.add(self.consoleBody)
        self.consoleBody.set_editable(False)
        self.table.attach(self.consoleFrame, 0, 1, 4, 5)

        self.setSaved()
        self.pipes = None

        self.window.show()

    def website(self, *args):
        webbrowser.open("http://bottersnike.github.io/Micro-Pi")

    def showAbout(self, *args):
        dia = gtk.AboutDialog()
        dia.set_property('program-name', 'Micro:Pi')
        dia.set_property('version', '0.0.1')
        dia.set_property('copyright', '(c) Nathan Taylor 2016')
        dia.set_property('website', 'http://bottersnike.github.io/Micro-Pi')
        dia.set_property('comments', 'A pure python IDE for the BBC:MicroBit for C++')
        dia.set_property('license', open('data/LICENSE').read())
        dia.show()
        dia.run()
        dia.destroy()
        return False

    def setUBitLoc(self, *args):
        loc = self.askQ("Location:", SETTINGS['mbitLocation'])
        if loc:
            SETTINGS['mbitLocation'] = loc
            saveSettings()

    def sendCopy(self, *args):
        s = self.notebook.get_nth_page(self.notebook.get_current_page())
        t = s.get_children()[0]
        t.emit("copy-clipboard")

    def sendPaste(self, *args):
        s = self.notebook.get_nth_page(self.notebook.get_current_page())
        t = s.get_children()[0]
        t.emit("paste-clipboard")

    def sendCut(self, *args):
        s = self.notebook.get_nth_page(self.notebook.get_current_page())
        t = s.get_children()[0]
        t.emit("cut-clipboard")

    def sendRedo(self, *args):
        s = self.notebook.get_nth_page(self.notebook.get_current_page())
        t = s.get_children()[0]
        t.emit("redo")

    def sendUndo(self, *args):
        s = self.notebook.get_nth_page(self.notebook.get_current_page())
        t = s.get_children()[0]
        t.emit("undo")

    def sendSelectAll(self, *args):
        s = self.notebook.get_nth_page(self.notebook.get_current_page())
        t = s.get_children()[0]
        t.emit("select-all", 1)

    def toggleQS(self, widget, *args):
        SETTINGS['quickstart'] = widget.get_active()
        saveSettings()

    def autoIndentToggle(self, widget, *args):
        self.autoIndent = widget.get_active()
        for f in self.notebook:
            f.get_child().set_auto_indent(widget.get_active())

    def lineNumbersToggle(self, widget, *args):
        self.lineNumbers = widget.get_active()
        for f in self.notebook:
            f.get_child().set_show_line_numbers(widget.get_active())

    def setTabWidth(self, widget, width, *args):
        if widget.get_active():
            self.tabWidth = width
            for f in self.notebook:
                f.get_child().set_tab_width(width)

    def addNotebookPage(self, title, content):
        area = gtk.ScrolledWindow()
        area.set_policy(gtk.POLICY_ALWAYS, gtk.POLICY_ALWAYS)
        area.show()

        txtB = gtkSourceView.Buffer()
        txtB.begin_not_undoable_action()
        txtB.set_style_scheme(self.style_scheme)
        txtB.set_language(self.language)
        txtB.set_highlight_matching_brackets(True)
        txtB.set_highlight_syntax(True)
        txtB.set_text(content)
        txtB.place_cursor(txtB.get_start_iter())
        txtB.set_modified(False)
        txtB.end_not_undoable_action()

        text = SourceView(txtB)
        text.set_tab_width(self.tabWidth)
        text.set_insert_spaces_instead_of_tabs(False)
        text.set_show_right_margin(True)
        text.set_show_line_marks(True)
        text.set_auto_indent(self.autoIndent)
        text.set_show_line_numbers(self.lineNumbers)
        text.show()
        text.modify_font(pango.FontDescription('Monospace 10'))
        area.add(text)
        top = gtk.HBox()
        title = gtk.Label(title)
        title.show()
        top.pack_start(title, True, True, 0)
        butt = gtk.Button()
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_CLOSE, 1)
        img.show()
        butt.set_image(img)
        butt.connect_object("clicked", self.closePage, area)
        top.pack_end(butt, True, True, 0)
        butt.show()
        top.show()
        self.notebook.append_page(area, top)

    def openFile(self, *args):
        if (not self.getModified()) or self.ask("There are unsaved files.\nContinue?"):
            fn = gtk.FileChooserDialog(title=None,
                                       action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                       buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            _filter = gtk.FileFilter()
            _filter.set_name("Micro:Pi Files")
            _filter.add_pattern("*.%s" % SETTINGS['fileExtention'])
            fn.add_filter(_filter)
            _filter = gtk.FileFilter()
            _filter.set_name("All Files")
            _filter.add_pattern("*")
            fn.add_filter(_filter)
            fn.show()

            resp = fn.run()
            if resp == gtk.RESPONSE_OK:
                text = open(fn.get_filename()).read()
                data = pickle.loads(text)
                try:
                    while len(self.notebook):
                        self.notebook.remove_page(0)
                    for page in data:
                        self.addNotebookPage(*page)
                    yes = True
                    self.saveLocation = fn.get_filename()
                    self.setSaved()
                except:
                    yes = False
            fn.destroy()
            if resp == gtk.RESPONSE_OK and not yes:
                self.message("File is not a Micro:Pi File")

    def save(self, *args):
        files = {}
        for f in self.notebook:
            fn = self.notebook.get_tab_label(f).get_children()[0].get_label()
            tb = f.get_child().get_buffer()
            txt = tb.get_text(*tb.get_bounds())
            files[fn] = txt
        data = pickle.dumps(files)
        if self.saveLocation:
            open(self.saveLocation, 'w').write(data)
            self.setSaved()
        else:
            self.saveAs()

    def saveAs(self, *args):
        fn = gtk.FileChooserDialog(title=None,
                                   action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                   buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        _filter = gtk.FileFilter()
        _filter.set_name("Micro:Pi Files")
        _filter.add_pattern("*.%s" % SETTINGS['fileExtention'])
        fn.add_filter(_filter)
        _filter = gtk.FileFilter()
        _filter.set_name("All Files")
        _filter.add_pattern("*")
        fn.add_filter(_filter)
        fn.show()

        resp = fn.run()

        files = []
        for f in self.notebook:
            fin = self.notebook.get_tab_label(f).get_children()[0].get_label()
            tb = f.get_child().get_buffer()
            txt = tb.get_text(*tb.get_bounds())
            files.append([fin, txt])
        data = pickle.dumps(files)

        if resp == gtk.RESPONSE_OK:
            open(fn.get_filename(), 'w').write(data)
            self.setSaved()
            self.saveLocation = fn.get_filename()
        fn.destroy()

    def destroy(self, *args):
        if (not self.getModified()) or self.ask("There are unsaved files.\nContinue?"):
            gtk.main_quit()
            return False
        return True

    def message(self, message):
        dia = gtk.MessageDialog(self.window, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, message)
        dia.show()
        dia.run()
        dia.destroy()
        return False

    def ask(self, query):
        dia = gtk.MessageDialog(self.window, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, query)
        dia.show()
        rtn=dia.run()
        dia.destroy()
        return rtn == gtk.RESPONSE_YES

    def askQ(self, query, prompt=None):
        if prompt:
            dia = EntryDialog(self.window, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, query, default_value=prompt)
        else:
            dia = EntryDialog(self.window, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, query)
        dia.show()
        rtn=dia.run()
        dia.destroy()
        return rtn

    def loadExample(self, example):
        if os.path.exists(os.path.join('examples', example)):
            if (not self.getModified()) or self.ask("There are unsaved files.\nContinue?"):
                text = open(os.path.join('examples', example)).read()
                try:
                    data = pickle.loads(text)
                    while len(self.notebook):
                        self.notebook.remove_page(0)
                    for page in data:
                        self.addNotebookPage(*page)
                    yes = True
                    self.setSaved()
                    self.saveLocation = ''
                except:
                    yes = False

    def newProject(self, *args):
        if (not self.getModified()) or self.ask("There are unsaved files.\nContinue?"):
            fileData = [('main.cpp', """#include "header.h"
#include "MicroBit.h"

void app_main()
{

}
"""), ('header.h', '')]
            while len(self.notebook):
                self.notebook.remove_page(0)
            for page in fileData:
                self.addNotebookPage(*page)

    def clearBuild(self):
        if os.path.exists(os.path.join(buildLocation, 'source/')):
            for i in os.listdir(os.path.join(buildLocation, 'source/')):
                os.remove(os.path.join(buildLocation, 'source/', i))
        delFolder(os.path.join(buildLocation,
                               'build/bbc-microbit-classic-gcc/source/'))

    def startBuild(self, *args):
        if not (self.mbedUploading or self.mbedBuilding):
            txtB = gtkSourceView.Buffer()
            txtB.set_style_scheme(self.style_scheme)
            txtB.set_highlight_matching_brackets(False)
            txtB.set_highlight_syntax(False)
            txtB.place_cursor(txtB.get_start_iter())

            self.consoleBody.props.buffer = txtB
            self.mbedBuilding = True
            self.clearBuild()
            for f in self.notebook:
                fn = self.notebook.get_tab_label(f).get_children()[0].get_label()
                tb = f.get_child().get_buffer()
                text = tb.get_text(*tb.get_bounds())
                open(os.path.join(buildLocation, 'source/%s' %
                                  fn), 'w').write(text)

            self.prevLoc = os.getcwd()
            os.chdir(buildLocation)
            os.environ['PWD'] = buildLocation

            if WINDOWS:
                p = Popen(
                    'cd %s & yotta --plain build' % buildLocation,
                    shell=True,
                    stderr=PIPE,
                    stdin=PIPE,
                    stdout=PIPE,
                    close_fds = True
                )
            else:
                p = Popen(
                    ['cd %s; yotta --plain build' % buildLocation],
                    shell=True,
                    stderr=PIPE,
                    stdin=PIPE,
                    stdout=PIPE,
                    close_fds = True
                )
            self.pipes = [p.stdin, NBSR(p.stdout, p), NBSR(p.stderr, p)]

    def startBuildAndUpload(self, *args):
        if not (self.mbedUploading or self.mbedBuilding):
            txtB = gtkSourceView.Buffer()
            txtB.set_style_scheme(self.style_scheme)
            txtB.set_highlight_matching_brackets(False)
            txtB.set_highlight_syntax(False)
            txtB.place_cursor(txtB.get_start_iter())

            self.consoleBody.props.buffer = txtB
            self.mbedBuilding = True
            self.mbedUploading = True
            self.clearBuild()
            for f in self.notebook:
                fn = self.notebook.get_tab_label(f).get_children()[0].get_label()
                tb = f.get_child().get_buffer()
                text = tb.get_text(*tb.get_bounds())
                open(os.path.join(buildLocation, 'source/%s' %
                                  fn), 'w').write(text)

            self.prevLoc = os.getcwd()
            os.chdir(buildLocation)
            os.environ['PWD'] = buildLocation

            if WINDOWS:
                p = Popen(
                    'cd %s & yotta --plain build' % buildLocation,
                    shell=True,
                    stderr=PIPE,
                    stdin=PIPE,
                    stdout=PIPE,
                    close_fds = True
                )
            else:
                p = Popen(
                    ['cd %s; yotta --plain build' % buildLocation],
                    shell=True,
                    stderr=PIPE,
                    stdin=PIPE,
                    stdout=PIPE,
                    close_fds = True
                )
            self.pipes = [p.stdin, NBSR(p.stdout, p), NBSR(p.stderr, p)]

    def importFile(self, *args):
        fn = gtk.FileChooserDialog(title=None,
                                   action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                   buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        _filter = gtk.FileFilter()
        _filter.set_name("C++ Files")
        _filter.add_pattern("*.cpp")
        _filter.add_pattern("*.h")
        fn.add_filter(_filter)
        _filter = gtk.FileFilter()
        _filter.set_name("All Files")
        _filter.add_pattern("*")
        fn.add_filter(_filter)
        fn.show()

        resp = fn.run()
        if resp == gtk.RESPONSE_OK:
            text = open(fn.get_filename()).read()

            self.addNotebookPage(os.path.basename(fn.get_filename()), text)

        fn.destroy()

    def forceUpload(self, *args):
        if os.path.exists('%s/build/bbc-microbit-classic-gcc/source/microbit-combined.hex' % buildLocation):
            if (not self.mbedBuilding) and (not self.mbedUploading):
                self.uBitUploading = True
                thread = Thread(target=upload, args=(self,))
                thread.daemon = True
                thread.start()

    def closePage(self, widget, *args):
        pn = self.notebook.page_num(widget)
        if (not widget.get_child().get_buffer().get_modified()) or self.ask("File Modified.\nDo you really want to close it?"):
            self.notebook.remove_page(pn)
            if self.notebook.get_n_pages() == 0:
                self.addNotebookPage('main.cpp', '')

    def newPage(self, *args):
        pageName = self.askQ("File Name")
        if pageName:
            self.addNotebookPage(pageName, '')

    def getModified(self):
        return any([i.get_child().get_buffer().get_modified() for i in self.notebook])

    def setSaved(self):
        for i in self.notebook:
            i.get_child().props.buffer.set_modified(False)

    def main(self):
        thread = Thread(target=uBitPoller, args=(self,))
        thread.daemon = True
        thread.start()
        thread = Thread(target=pipePoller, args=(self,))
        thread.daemon = True
        thread.start()
        thread = Thread(target=updateTitle, args=(self,))
        thread.daemon = True
        thread.start()
        gtk.main()

class SerialConsole:
    def __init__(self):
        self.imageCreator = ImageCreator()

        self.baudrate = 115200
        self.ports = list(list_ports.grep(''))
        self.serialLocation = self.ports[0][0] if self.ports else None
        self.serialConnection = None if not self.serialLocation else serial.serial_for_url(self.serialLocation)
        if self.serialLocation is not None:
            self.serialConnection.baudrate = self.baudrate

        thread = Thread(target=serialPoller, args=(self,))
        thread.daemon = True
        thread.start()

        mgr = gtkSourceView.style_scheme_manager_get_default()
        self.style_scheme = mgr.get_scheme('oblivion')

        self.window = gtk.Window()
        self.window.set_title('Serial Monitor')
        self.window.set_icon_from_file('data/icon.png')
        self.window.resize(750, 400)
        colour = gtk.gdk.color_parse('#242424')
        self.window.modify_bg(gtk.STATE_NORMAL, colour)

        self.vbox = gtk.VBox()
        self.vbox.show()

        self.consoleFrame = gtk.ScrolledWindow()
        self.consoleFrame.set_policy(gtk.POLICY_ALWAYS, gtk.POLICY_ALWAYS)
        self.consoleFrame.show()

        txtB = gtkSourceView.Buffer()
        txtB.set_style_scheme(self.style_scheme)
        txtB.set_highlight_matching_brackets(False)
        txtB.set_highlight_syntax(False)
        txtB.place_cursor(txtB.get_start_iter())

        self.consoleBody = SourceView(txtB)
        self.consoleBody.modify_font(pango.FontDescription('Monospace 10'))
        self.consoleBody.show()
        self.consoleFrame.add(self.consoleBody)
        self.consoleBody.set_editable(False)
        self.vbox.pack_start(self.consoleFrame, 2)

        self.entryHBox = gtk.HBox()
        self.entry = gtk.Entry()
        self.entryHBox.pack_start(self.entry, True, True, 2)
        self.entry.show()
        self.entry.connect("activate", self.send)
        self.sendButton = gtk.Button("Send")
        self.entryHBox.pack_start(self.sendButton, False, False, 2)
        self.sendButton.show()
        self.sendButton.connect("clicked", self.send)
        self.sendImageButton = gtk.Button("Send Image")
        self.entryHBox.pack_start(self.sendImageButton, False, False, 2)
        self.sendImageButton.show()
        self.sendImageButton.connect("clicked", self.showImageCreator)

        self.entryHBox.show()
        self.vbox.pack_start(self.entryHBox, False, False, 2)

        self.hbox = gtk.HBox()
        self.hbox.show()
        self.gtkbaudrate = gtk.combo_box_new_text()
        self.gtkbaudrate.append_text('300')
        self.gtkbaudrate.append_text('1200')
        self.gtkbaudrate.append_text('2400')
        self.gtkbaudrate.append_text('4800')
        self.gtkbaudrate.append_text('9600')
        self.gtkbaudrate.append_text('19200')
        self.gtkbaudrate.append_text('38400')
        self.gtkbaudrate.append_text('57600')
        self.gtkbaudrate.append_text('115200')
        self.gtkbaudrate.show()
        self.gtkbaudrate.set_active(8)
        self.gtkbaudrate.connect('changed', self.brtchange)
        self.hbox.pack_start(self.gtkbaudrate, False, False)

        self.refreshButton = gtk.Button("Refresh")
        self.refreshButton.show()
        self.refreshButton.connect('clicked', self.refresh)
        self.hbox.pack_start(self.refreshButton, True, False)

        self.clearButton = gtk.Button("Clear")
        self.clearButton.show()
        self.clearButton.connect('clicked', self.clear)
        self.hbox.pack_start(self.clearButton, True, False)

        self.gtkserialloc = gtk.combo_box_new_text()
        for i in self.ports:
            self.gtkserialloc.append_text(i[0])
        self.gtkserialloc.show()
        self.gtkserialloc.set_active(0)
        self.gtkserialloc.connect('changed', self.portchange)
        self.gtkserialloc.show()
        self.hbox.pack_end(self.gtkserialloc, False, False)
        self.vbox.pack_start(self.hbox, False, False, 0)

        self.window.add(self.vbox)

        self.shown = False

        self.window.connect("delete_event", self.destroy)

    def send(self, *args):
        if self.serialConnection:
            self.serialConnection.write(self.entry.get_text() + '\n')
        self.entry.set_text('')

    def clear(self, *args):
        txtB = gtkSourceView.Buffer()
        txtB.set_style_scheme(self.style_scheme)
        txtB.set_highlight_matching_brackets(False)
        txtB.set_highlight_syntax(False)
        txtB.place_cursor(txtB.get_start_iter())
        self.consoleBody.set_buffer(txtB)

    def refresh(self, *args):
        self.ports = list(list_ports.grep(''))
        self.serialLocation = self.ports[0][0] if self.ports else None
        self.serialConnection = None if not self.serialLocation else serial.serial_for_url(self.serialLocation)
        if self.serialLocation is not None:
            self.serialConnection.baudrate = self.baudrate
        self.gtkserialloc.get_model().clear()
        for i in self.ports:
            self.gtkserialloc.append_text(i[0])
        self.gtkserialloc.set_active(0 if self.ports else -1)

    def brtchange(self, widget, *args):
        model = widget.get_model()
        index = widget.get_active()
        newbdrate = int(model[index][0])
        self.baudrate = newbdrate
        if not self.serialConnection:
            self.serialConnection = serial.serial_for_url(self.serialLocation)
        self.serialConnection.baudrate = newbdrate

    def portchange(self, widget, *args):
        model = widget.get_model()
        index = widget.get_active()
        if 0 <= index < len(model):
            newport = model[index][0]
            self.serialLocation = newport
            if not self.serialConnection:
                self.serialConnection = serial.serial_for_url(self.serialLocation)
            self.serialConnection.port = newport
            self.serialConnection.baudrate = self.baudrate

    def destroy(self, *args):
        self.window.hide()
        self.shown = False
        return True

    def toggleVis(self, *args):
        if self.shown:
            self.shown = False
            self.window.hide()
        else:
            self.shown = True
            #self.serialLocation = list(list_ports.grep(''))[0][0]
            txtB = gtkSourceView.Buffer()
            txtB.set_style_scheme(self.style_scheme)
            txtB.set_highlight_matching_brackets(False)
            txtB.set_highlight_syntax(False)
            txtB.place_cursor(txtB.get_start_iter())
            self.consoleBody.set_buffer(txtB)
            #self.serialConnection = serial.serial_for_url(self.serialLocation)
            #self.serialConnection.baudrate = self.baudrate
            self.window.show()

    def insertImage(self, image, *args):
        if self.serialConnection:
            self.serialConnection.write(image)

    def showImageCreator(self, *args):
        self.imageCreator.show(self.insertImage)

class ImageCreator():

    def __init__(self, *args, **kwargs):
        self.window = gtk.Window()
        self.window.set_title('Create An Image')
        self.window.set_icon_from_file('data/icon.png')
        colour = gtk.gdk.color_parse('#242424')
        self.window.modify_bg(gtk.STATE_NORMAL, colour)

        self.vvbox = gtk.VBox()
        self.table = gtk.Table(5, 5)
        self.table.set_border_width(2)
        self.table.set_row_spacings(2)
        self.table.set_col_spacings(2)
        self.buttons = {}

        for y in range(5):
            for x in range(5):
                eb = gtk.EventBox()
                i = gtk.Image()
                i.set_from_file('data/selected.png')
                i.show()
                eb.add(i)
                eb.hide()
                eb.modify_bg(gtk.STATE_NORMAL, colour)
                eb.connect_object('button-press-event', self.togglePart, (x, y))

                eb2 = gtk.EventBox()
                i2 = gtk.Image()
                i2.set_from_file('data/unselected.png')
                i2.show()
                eb2.add(i2)
                eb2.show()
                eb2.modify_bg(gtk.STATE_NORMAL, colour)
                eb2.connect_object('button-press-event', self.togglePart, (x, y))

                self.buttons[(x, y)] = (eb, eb2)

                self.table.attach(eb, x, x + 1, y, y + 1)
                self.table.attach(eb2, x, x + 1, y, y + 1)

        self.table.show()
        self.vvbox.pack_start(self.table)
        hbox = gtk.HBox()
        self.confirmButton = gtk.Button("Okay")
        self.confirmButton.show()
        self.confirmButton.connect("clicked", self.okay)
        hbox.pack_start(self.confirmButton, True, False)
        cancelButton = gtk.Button("Cancel")
        cancelButton.connect("clicked", self.destroy)
        cancelButton.show()
        hbox.pack_end(cancelButton, True, False)
        hbox.show()
        self.vvbox.pack_start(hbox)
        self.vvbox.show()
        self.window.add(self.vvbox)
        self.onOkay = None

        self.running = True
        self.destoryed = False

    def destroy(self, *args):
        self.window.hide()

    def okay(self, *args):
        data = ''
        self.window.hide()
        for y in range(5):
            line = []
            for x in range(5):
                line.append(str(int(self.buttons[(x, y)][0].props.visible)))
            data += ','.join(line) + '\n'
        if self.onOkay:
            self.onOkay(data)

    def show(self, onOkay, *args):
        for i in self.buttons:
            self.buttons[i][1].show()
            self.buttons[i][0].hide()
        self.onOkay = onOkay
        self.window.show()

    def hide(self, *args):
        self.window.hide()

    def togglePart(self, pos, *args):
        if self.buttons[pos][0].props.visible:
            self.buttons[pos][0].hide()
            self.buttons[pos][1].show()
        else:
            self.buttons[pos][1].hide()
            self.buttons[pos][0].show()

class FullscreenToggler(object):
    def __init__(self, window, keysym=gtk.keysyms.F11):
        self.window = window
        self.keysym = keysym
        self.window_is_fullscreen = False
        self.window.connect_object('window-state-event', FullscreenToggler.on_window_state_change, self)
    def on_window_state_change(self, event):
        self.window_is_fullscreen = bool(gtk.gdk.WINDOW_STATE_FULLSCREEN & event.new_window_state)
    def toggle(self, event):
        if event.keyval == self.keysym:
            if self.window_is_fullscreen:
                self.window.unfullscreen()
            else:
                self.window.fullscreen()

class SplashScreen:
    def __init__(self):
        imageLoc = random.choice(os.listdir('data/splashScreens'))
        imageSize = self.get_image_size(open(os.path.join('data/splashScreens', imageLoc), 'rb').read())

        self.window = gtk.Window(gtk.WINDOW_POPUP)
        self.window.set_title("Micro:Pi")
        self.window.set_size_request(imageSize[0], -1)
        #colour = gtk.gdk.color_parse('#242424')
        #self.window.modify_bg(gtk.STATE_NORMAL, colour)
        self.window.set_position(gtk.WIN_POS_CENTER)
        main_vbox = gtk.VBox(False, 1)
        self.window.add(main_vbox)
        hbox = gtk.HBox(False, 0)
        self.img = gtk.Image()
        self.img.set_from_file(os.path.join('data/splashScreens', imageLoc))
        main_vbox.pack_start(self.img, True, True)
        self.lbl = gtk.Label('')
        font = pango.FontDescription('Monospace 7')
        self.lbl.modify_font(font)
        main_vbox.pack_end(self.lbl, False, False)
        self.window.show_all()
    def get_image_size(self, data):
        def is_png(data):
            return (data[:8] == '\211PNG\r\n\032\n' and (data[12:16] == 'IHDR'))
        if is_png(data):
            w, h = struct.unpack('>LL', data[16:24])
            width = int(w)
            height = int(h)
            return width, height
        return -1, -1
    def set_text(self, text):
        self.lbl.props.label = text
        self.refresh()
    def refresh(self):
        while gtk.events_pending():
            gtk.main_iteration()

if __name__ == "__main__":

    ss = SplashScreen()

    ss.set_text('')

    try:
        HOMEDIR = os.path.expanduser('~')
        MICROPIDIR = os.path.join(HOMEDIR, '.micropi')#-' + sys.version.split(' ')[0])

        def delFolder(path):
            if os.path.exists(path):
                for i in os.listdir(path):
                    if os.path.isdir(os.path.join(path, i)):
                        delFolder(os.path.join(path, i))
                        os.rmdir(os.path.join(path, i))
                    else:
                        os.remove(os.path.join(path, i))

        FIRSTRUN = False

        TABSIZE = 4

        WINDOWS = os.name == 'nt'

        def copyDir(path, newPath):
            os.mkdir(newPath)
            for i in os.listdir(path):
                sys.stdout.write(os.path.join(path, i) + '\n')
                if os.path.isdir(os.path.join(path, i)):
                    copyDir(os.path.join(path, i), os.path.join(newPath, i))
                else:
                    d = open(os.path.join(path, i)).read()
                    open(os.path.join(newPath, i), 'w').write(d)

        if not os.path.exists(MICROPIDIR):
            os.mkdir(MICROPIDIR)

        defualtConfig = """quickstart: %s
mbitLocation: "%s"
fileExtention: "mpi\""""
        if not os.path.exists(os.path.join(MICROPIDIR, 'config.conf')):
            res = ask("Enable Quick Start?")
            res2 = askQ("Micro:Bit Location")
            if not res2:
                res2 = "/media/MICROBIT"
            ss.set_text("Creating Config")
            print("Creating Config")

            open(os.path.join(MICROPIDIR, 'config.conf'),
                 'w').write(defualtConfig % (str(res), res2))
        configLocation = os.path.join(MICROPIDIR, 'config.conf')

        if not os.path.exists(os.path.join(HOMEDIR, 'Documents')):
            os.mkdir(os.path.join(HOMEDIR, 'Documents'))
        if not os.path.exists(os.path.join(HOMEDIR, 'Documents', 'MicroPi Projects')):
            os.mkdir(os.path.join(HOMEDIR, 'Documents', 'MicroPi Projects'))
        SAVEDIR = os.path.join(HOMEDIR, 'Documents', 'MicroPi Projects')

        if not os.path.exists(os.path.join(MICROPIDIR, 'buildEnv')):
            FIRSTRUN = True
            ss.set_text("Installing Build Enviroment")
            print("Installing Build Enviroment")

            f = tempfile.mktemp()
            open(f, 'wb').write(base64.b64decode(buildenv.benv.replace('\n', '')))
            tf = tarfile.open(f, 'r:gz')
            tf.extractall(MICROPIDIR)
            os.remove(f)

        buildLocation = os.path.join(MICROPIDIR, 'buildEnv')

        SETTINGS = {}
        d = open(configLocation).read().split('\n')
        for i in d:
            i2 = i.split(':')
            if i:
                SETTINGS[i[:len(i2[0])]] = eval(i[len(i2[0]) + 1:])

        def rstbuild():
            delFolder(os.path.join(buildLocation, 'build'))

        if not SETTINGS['quickstart'] or FIRSTRUN:
            rstbuild()
        prevLoc = os.getcwd()
        os.chdir(buildLocation)
        os.environ['PWD'] = buildLocation
        os.system('yotta target bbc-microbit-classic-gcc')
        if not SETTINGS['quickstart'] or FIRSTRUN:
            _file = """#include "MicroBit.h"

    void app_main()
    {
    while (1)
    {
        uBit.sleep(100);
    }
    }
    """

            open('source/main.cpp', 'w').write(_file)
            if WINDOWS:
                p = Popen(
                    'cd %s & yotta --plain build' % buildLocation,
                    shell=True,
                    stderr=PIPE,
                    stdin=PIPE,
                    stdout=PIPE,
                    close_fds = True
                )
            else:
                p = Popen(
                    ['cd %s; yotta --plain build' % buildLocation],
                    shell=True,
                    stderr=PIPE,
                    stdin=PIPE,
                    stdout=PIPE,
                    close_fds = True
                )
            pipes = [p.stdin, NBSR(p.stdout, p), NBSR(p.stderr, p)]

            while pipes:
                try:
                    d1 = pipes[1].readline()
                    d2 = pipes[2].readline()
                except UnexpectedEndOfStream:
                    pass

                if type(d1) != str:
                    d1 = str(d1, encoding="utf-8")
                if type(d2) != str:
                    d2 = str(d2, encoding="utf-8")

                if d1:
                    ss.set_text(d1[:-1])
                if d2:
                    ss.set_text(d2[:-1])

                if not (pipes[1].alive()) or (not pipes[2].alive()):
                    pipes = None
        os.chdir(prevLoc)

    except Exception as e:
        import traceback
        print traceback.print_exc()
    main = MainWin()
    ss.window.destroy()
    main.main()
