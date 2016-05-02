#  micropigtk.py
#
#  Copyright 2016  <pi@raspberrypi>
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
import pygtk
pygtk.require('2.0')
import gtk
gtk.threads_init()
import pango
import pickle
from threading import Thread
import time
import os
from subprocess import PIPE, Popen
from gtksourceview2 import View as SourceView
import gtksourceview2 as gtkSourceView
from Queue import Queue, Empty

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

    defualtConfig = """darkHighlight: (50, 130, 50)
quickstart: %s
mbitLocation: "%s"
lightbgColour: (36, 36, 36)
theme: "darkgreen"
highlightColour: (73, 182, 73)
backgroundColour: (36, 36, 36)
fileExtention: "mpi\""""
    if not os.path.exists(os.path.join(MICROPIDIR, 'config.conf')):

        root = tk.Tk()
        root.withdraw()
        res = msgbox.askyesno("Settings", "Enable Quick Start?")
        res2 = simpd.askstring("Settings", "Micro:Bit Location")
        if not res2:
            res2 = "/media/MICROBIT"
        root.destroy()
        print("Creating Config")

        screen.blit(img, (0, 0))
        t = font.render("Creating Config", 1, (73, 182, 73))
        screen.blit(t, (0, img.get_height() - t.get_height()))
        pygame.display.flip()
        pygame.event.get()

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
        print("Installing Build Enviroment")

        screen.blit(img, (0, 0))
        t = font.render("Installing Build Enviroment", 1, (73, 182, 73))
        screen.blit(t, (0, img.get_height() - t.get_height()))
        pygame.display.flip()
        pygame.event.get()

        f = tempfile.mktemp()
        try:
            open(f, 'wb').write(base64.b64decode(buildenv.benv.replace('\n', '')))
        except:
            __f = open(f, 'wb')
            __f.buffer.write(base64.b64decode(buildenv.benv.replace('\n', '')))
            __f.close()
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

    t = time.localtime()
    val = '%d-%d-%d-%d' % (t.tm_hour, t.tm_wday, t.tm_mon, t.tm_year)
    LOGDIR = os.path.join(MICROPIDIR, 'logs')
    if not os.path.exists(LOGDIR):
        os.mkdir(LOGDIR)
    logging.basicConfig(
        level=logging.DEBUG,
        filename="%s/%s.log" % (LOGDIR, val),
        format="[%(levelname)s][%(relativeCreated)d] %(message)s"
    )
except:
    pass

def uBitPoller(self):
    last = (False, False)
    while True:
        self.uBitFound = os.path.exists(SETTINGS['mbitLocation'])
        if not (self.uBitUploading and self.uBitFound):
            if self.uBitFound and not last[0]:
                gtk.idle_add(self.indicator.set_from_file, "data/uBitFound.png")
            elif last[0] and not self.uBitFound:
                gtk.idle_add(self.indicator.set_from_file, "data/uBitNotFound.png")
                self.uBitUploading = False
        else:
            gtk.idle_add(self.indicator.set_from_file, "data/uBitUploading.png")
        time.sleep(2)
        last = (self.uBitFound, self.uBitUploading)

def pipePoller(self):
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

            if not (self.pipes[1].alive() or self.pipes[2].alive()):
                self.pipes = None
                self.mbedBuilding = False
                os.chdir(self.prevLoc)
                if os.path.exists('%s/build/bbc-microbit-classic-gcc/source/microbit-combined.hex' % buildLocation):
                    tb = self.consoleBody.get_buffer()
                    tb.insert(tb.get_end_iter(), "Done!\n")
                    if self.mbedUploading and self.uBitFound:
                        tb = self.consoleBody.get_buffer()
                        tb.insert(tb.get_end_iter(), "Uploading!\n")
                        self.uBitUploading = True
                        thread = Thread(target=upload, args=(self,))
                        thread.daemon = True
                        thread.start()
                    elif self.mbedUploading:
                        self.uBitUploading = False
                        self.mbedUploading = False
                        self.message("""Cannot upload!
Micro:Bit not found!
Check it is plugged in and
Micro:Pi knows where to find it.""")
                else:
                    self.message("""There is an error
with your code!
It is advised to scroll
back through the console
to find out what the error is!""")
                    self.uBitUploading = False
                    self.mbedUploading = False
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

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.fullscreenToggler = FullscreenToggler(self.window)
        self.window.connect_object('key-press-event', FullscreenToggler.toggle, self.fullscreenToggler)
        self.window.set_title('Micro:Pi')
        self.window.set_icon_from_file('data/icon.png')
        self.window.resize(750, 500)
        colour = gtk.gdk.color_parse('#242424')
        self.window.modify_bg(gtk.STATE_NORMAL, colour)

        self.window.connect("delete_event", self.destroy)
        #self.window.connect("destroy", self.destroy)

        self.table = gtk.Table(5, 1, False)
        self.table.show()
        self.window.add(self.table)

        self.uBitUploading = False
        self.mbedBuilding = False
        self.mbedUploading = False
        self.uBitFound = False

        self.tabWidth = 4

        self.saveLocation = ''

        exampleMenu = [(i[:-4] if i[-4:] == '.mpi' else i, (self.loadExample, '', '', i))
                   for i in os.listdir('examples')]
        menuData = [
                    ("_File", [
                              ("_New Project", ('', gtk.STOCK_NEW, '<Control>N')),
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
                    ("_View", [
                               ("Show _Line Numbers", (self.testCheck, '', '', '', 'checkbox', True)),
                               ("Enable Auto _Indent", (self.testCheck, '', '', '', 'checkbox', True)),
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
                               ]

                    )
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
        tbW.pack_start(self.toolbar)
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

    def testCheck(self, widget, *args):
        print widget.get_active()

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
        txtB.set_style_scheme(self.style_scheme)
        txtB.set_language(self.language)
        txtB.set_highlight_matching_brackets(True)
        txtB.set_highlight_syntax(True)
        txtB.set_text(content)
        txtB.place_cursor(txtB.get_start_iter())

        text = SourceView(txtB)
        text.set_tab_width(self.tabWidth)
        text.set_insert_spaces_instead_of_tabs(True)
        text.show()
        text.modify_font(pango.FontDescription('Monospace 10'))
        area.add(text)
        top = gtk.HBox()
        title = gtk.Label(title)
        title.show()
        top.pack_start(title)
        butt = gtk.Button()
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_CLOSE, 1)
        img.show()
        butt.set_image(img)
        butt.connect_object("clicked", self.closePage, area)
        top.pack_end(butt)
        butt.show()
        top.show()
        self.notebook.append_page(area, top)

    def openFile(self, *args):
        fn = gtk.FileChooserDialog(title=None,
                                   action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                   buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        _filter = gtk.FileFilter()
        _filter.set_name("Micro:Pi Files")
        _filter.add_pattern("*.mpi")
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
        _filter.add_pattern("*.mpi")
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
        dia = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, message)
        dia.show()
        dia.run()
        dia.destroy()

    def ask(self, query):
        dia = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, query)
        dia.show()
        rtn=dia.run()
        dia.destroy()
        return rtn == gtk.RESPONSE_YES

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

    def clearBuild(self):
        if os.path.exists(os.path.join(buildLocation, 'source/')):
            for i in os.listdir(os.path.join(buildLocation, 'source/')):
                os.remove(os.path.join(buildLocation, 'source/', i))

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
        self.notebook.remove_page(pn)
        if self.notebook.get_n_pages() == 0:
            self.addNotebookPage('main.cpp', '')

    def newPage(self, *args):
        self.addNotebookPage(':)', '')

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

if __name__ == "__main__":
    main = MainWin()
    main.main()
