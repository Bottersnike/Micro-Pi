
class MainWin:
    def __init__(self, fileData=None):
        self.active = True
        mgr = gtkSourceView.style_scheme_manager_get_default()
        self.style_scheme = mgr.get_scheme('tango' if SETTINGS['theme']=='light' else 'oblivion')
        self.language_manager = gtkSourceView.language_manager_get_default()
        self.languages = {}
        for i in self.language_manager.get_language_ids():
            self.languages[i] = self.language_manager.get_language(i)
        self.filetypes = loadConfig(os.path.join(WORKINGDIR, "data", "filetypes.conf"))

        self.window = gtk.Window()
        self.fullscreenToggler = FullscreenToggler(self.window)
        self.window.connect_object('key-press-event', FullscreenToggler.toggle, self.fullscreenToggler)
        self.window.set_title('Micro:Pi')
        self.window.set_icon_from_file(os.path.join(WORKINGDIR, "data", "icon.png"))
        self.window.resize(750, 500)
        #if SETTINGS['theme'] == 'dark':
            #colour = gtk.gdk.color_parse(DARKCOL)
        #else:
            #colour = gtk.gdk.color_parse(LIGHTCOL)
        #self.window.modify_bg(gtk.STATE_NORMAL, colour)

        self.window.connect("delete_event", self.destroy)

        self.serialConsole = SerialConsole()

        self.table = gtk.Table(5, 1, False)
        self.table.show()
        self.window.add(self.table)

        self.tabWidth = 4
        self.autoIndent = True
        self.lineNumbers = True

        self.saveLocation = ''

        def loadEXPMen(path):
            men = []
            p = os.listdir(path)
            p.sort()
            for i in p:
                if not os.path.isdir(os.path.join(path, i)):
                    if i[-(len(SETTINGS['fileExtention'])+1):] == '.'+SETTINGS['fileExtention']:
                        ni = i[:-(len(SETTINGS['fileExtention'])+1)]
                    else:
                        ni = i
                    men.append((ni, (self.loadExample, '', '', os.path.join(path, i))))
                else:
                    men.append((i, loadEXPMen(os.path.join(path, i))))
            return men

        #exampleMenu = [(i[:-(len(SETTINGS['fileExtention'])+1)] if i[-(len(SETTINGS['fileExtention'])+1):] == '.'+SETTINGS['fileExtention'] else i, (self.loadExample, '', '', i))
                   #for i in os.listdir('examples')]
        exampleMenu = loadEXPMen(os.path.join(WORKINGDIR, "examples"))

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
                               ("Preference_s", (self.showSettings, gtk.STOCK_PREFERENCES, '<Control><Alt>P'))
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
        self.indicator.set_from_file(os.path.join(WORKINGDIR, "data", "uBitNotFound.png"))
        self.indicator.show()
        self.toolbar.pack_start(self.indicator, False)


        self.toolbar.show()
        tbW.pack_start(self.toolbar, True, True, 0)
        tbW.show()
        self.table.attach(tbW, 0, 5, 1, 2, gtk.FILL, gtk.FILL)

        self.notebook = gtk.Notebook()
        #self.table.attach(self.notebook, 0, 1, 2, 4)
        self.notebook.show()
        if not fileData:
            fileData = [('main.cpp', """#include "MicroBit.h"

MicroBit uBit;

int main()
{
    uBit.init();

    while (1)
    {

    }
}
""")]
        elif type(fileData) == dict:
            fd = []
            for i in fileData:
                fd.append((i, fileData[i]))
            fileData = fd
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
        #self.table.attach(self.consoleFrame, 0, 1, 4, 5)

        self.bodyPaned = gtk.VPaned()
        self.bodyPaned.pack1(self.notebook, True, True)
        self.bodyPaned.pack2(self.consoleFrame, False, True)
        self.table.attach(self.bodyPaned, 0, 1, 2, 5)
        self.bodyPaned.show()

        self.setSaved()

        self.setTheme(None, SETTINGS['theme'])

        if SETTINGS['theme'] == 'dark':
            colour = gtk.gdk.color_parse(DARKCOL)
        else:
            colour = gtk.gdk.color_parse(LIGHTCOL)

        self.window.modify_bg(gtk.STATE_NORMAL, colour)

        mgr = gtkSourceView.style_scheme_manager_get_default()
        self.style_scheme = mgr.get_scheme('tango' if SETTINGS['theme']=='light' else 'oblivion')
        for f in self.notebook:
            f.get_child().props.buffer.set_style_scheme(self.style_scheme)
        self.serialConsole.window.modify_bg(gtk.STATE_NORMAL, colour)
        if SENDIMAGE: self.serialConsole.imageCreator.window.modify_bg(gtk.STATE_NORMAL, colour)
        self.serialConsole.consoleBody.props.buffer.set_style_scheme(self.style_scheme)
        self.consoleBody.props.buffer.set_style_scheme(self.style_scheme)

        self.window.show()

        if len(sys.argv) > 1:
            self.forceOpenFileByFN(sys.argv[1])

    def website(self, *args):
        webbrowser.open("http://bottersnike.github.io/Micro-Pi")

    def showAbout(self, *args):
        dia = gtk.AboutDialog()
        dia.set_property('program-name', 'Micro:Pi')
        dia.set_property('version', '0.0.1')
        dia.set_property('copyright', '(c) Nathan Taylor 2016\nThe words "BBC" and "Micro:Bit" and the BBC Micro:Bit logo are all\ntrademarks of the BBC and I lay no claim to them.')
        dia.set_property('website', 'http://bottersnike.github.io/Micro-Pi')
        dia.set_property('comments', 'A pure python IDE for the BBC:MicroBit for C++')
        dia.set_property('license', open('data", "LICENSE').read())
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

    def setTheme(self, widget, theme, *args):
        if widget is None or widget.get_active():
            SETTINGS['theme'] = theme
            saveSettings()
            if SETTINGS['theme'] == 'dark':
                colour = gtk.gdk.color_parse(DARKCOL)
            else:
                colour = gtk.gdk.color_parse(LIGHTCOL)

            for w in OPENWINDOWS:
                w.window.modify_bg(gtk.STATE_NORMAL, colour)

                mgr = gtkSourceView.style_scheme_manager_get_default()
                w.style_scheme = mgr.get_scheme('tango' if SETTINGS['theme']=='light' else 'oblivion')
                for f in self.notebook:
                    f.get_child().props.buffer.set_style_scheme(self.style_scheme)
                w.serialConsole.window.modify_bg(gtk.STATE_NORMAL, colour)
                if SENDIMAGE: w.serialConsole.imageCreator.window.modify_bg(gtk.STATE_NORMAL, colour)
                w.serialConsole.consoleBody.props.buffer.set_style_scheme(w.style_scheme)
                w.consoleBody.props.buffer.set_style_scheme(w.style_scheme)

    def getLanguage(self, title):
        for a, b in self.filetypes.items():
            for i in b.split(';'):
                if fnmatch.filter([title], i):
                    a = a.lower()
                    if a in self.languages:
                        return self.languages[a]
        return None

    def addNotebookPage(self, title, content):
        area = gtk.ScrolledWindow()
        area.set_policy(gtk.POLICY_ALWAYS, gtk.POLICY_ALWAYS)
        area.show()

        txtB = gtkSourceView.Buffer()
        txtB.begin_not_undoable_action()
        txtB.set_style_scheme(self.style_scheme)

        language = self.getLanguage(title)

        txtB.set_highlight_matching_brackets(True)
        if language is not None:
            txtB.set_highlight_syntax(True)
            txtB.set_language(language)

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
            fn = gtk.FileChooserDialog(title="Save File",
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
                try:
                    text = open(fn.get_filename()).read()
                    try:
                        d = text.replace("\n", "")
                        d = base64.b64decode(d)
                        data = pickle.loads(d)
                    except:
                        data = pickle.loads(text)
                    mw = MainWin(data)
                    yes = True
                    mw.saveLocation = fn.get_filename()
                    mw.setSaved()
                    OPENWINDOWS.append(mw)
                except:
                    yes = False
            fn.destroy()
            if resp == gtk.RESPONSE_OK and not yes:
                self.message("File is not a Micro:Pi File")

    def forceOpenFileByFN(self, fn, *args):
        yes = True
        try:
            try:
                text = open(fn).read()
            except:
                fn = os.path.join(WORKINGDIR, fn)
                text = open(fn).read()
            try:
                d = text.replace("\n", "")
                d = base64.b64decode(d)
                data = pickle.loads(d)
            except:
                data = pickle.loads(text)
            sys.argv = [sys.argv[0]]
            mw = MainWin(data)
            mw.saveLocation = fn
            mw.setSaved()
            OPENWINDOWS.append(mw)
            self.destroy()
            yes = True
        except:
            yes = False
        if not yes:
            self.message("File is not a Micro:Pi File")

    def save(self, *args):
        files = {}
        for f in self.notebook:
            fn = self.notebook.get_tab_label(f).get_children()[0].get_label()
            tb = f.get_child().get_buffer()
            txt = tb.get_text(*tb.get_bounds())
            files[fn] = txt
        data = base64.b64encode(pickle.dumps(files))
        data = "".join(data[i:i+64]+"\n" for i in xrange(0, len(data), 64))
        if self.saveLocation:
            open(self.saveLocation, 'w').write(data)
            self.setSaved()
        else:
            self.saveAs()

    def saveAs(self, *args):
        fn = gtk.FileChooserDialog(title="Save File As",
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
        data = base64.b64encode(pickle.dumps(files))
        data = "".join(data[i:i+64]+"\n" for i in xrange(0, len(data), 64))

        if resp == gtk.RESPONSE_OK:
            fp = fn.get_filename()
            if fp[-(len(SETTINGS["fileExtention"])+1):] != "." + SETTINGS["fileExtention"]:
                fp += "." + SETTINGS["fileExtention"]
            open(fp, 'w').write(data)
            self.setSaved()
            self.saveLocation = fp
        fn.destroy()

    def destroy(self, *args):
        if (not self.getModified()) or self.ask("There are unsaved files.\nContinue?"):
            self.active = False
            self.window.hide()
            kill = True
            for i in OPENWINDOWS:
                if i.active:
                    kill = False
            if kill:
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
            dia = EntryDialog(self.window, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, query, default_value=prompt)
        else:
            dia = EntryDialog(self.window, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, query)
        dia.show()
        rtn=dia.run()
        dia.destroy()
        return rtn

    def loadExample(self, example):
        if os.path.exists(os.path.join(WORKINGDIR, example)):
            #if (not self.getModified()) or self.ask("There are unsaved files.\nContinue?"):
            text = open(example).read()
            try:
                try:
                    data = pickle.loads(base64.b64decode(text.replace("\n", "")))
                except Exception as e:
                    data = pickle.loads(text)

                mw = MainWin(data)
                yes = True
                mw.saveLocation = ''
                mw.setSaved()
                OPENWINDOWS.append(mw)
            except:
                yes = False

    def newProject(self, *args):
        #if (not self.getModified()) or self.ask("There are unsaved files.\nContinue?"):
        fileData = [("main.cpp", """#include "header.h"
#include "MicroBit.h"

void app_main()
{

}
"""), ('header.h', '')]
        mw = MainWin(fileData)
        mw.saveLocation = ''
        mw.setSaved()
        OPENWINDOWS.append(mw)

    def clearBuild(self):
        if os.path.exists(os.path.join(buildLocation, "source/")):
            for i in os.listdir(os.path.join(buildLocation, "source/")):
                os.remove(os.path.join(buildLocation, "source/", i))
        delFolder(os.path.join(buildLocation,
                               "build/bbc-microbit-classic-gcc/source/"))

    def startBuild(self, *args):
        global mbedUploading
        global mbedBuilding
        global uBitUploading
        global uBitFound
        global pipes
        if not (mbedUploading or mbedBuilding):
            for w in OPENWINDOWS:
                txtB = gtkSourceView.Buffer()
                txtB.set_style_scheme(self.style_scheme)
                txtB.set_highlight_matching_brackets(False)
                txtB.set_highlight_syntax(False)
                txtB.place_cursor(txtB.get_start_iter())

                w.consoleBody.props.buffer = txtB
            mbedBuilding = True
            self.clearBuild()
            for f in self.notebook:
                fn = self.notebook.get_tab_label(f).get_children()[0].get_label()
                tb = f.get_child().get_buffer()
                text = tb.get_text(*tb.get_bounds())
                open(os.path.join(buildLocation, "source/%s" %
                                  fn), 'w').write(text)

            os.chdir(buildLocation)
            os.environ["PWD"] = buildLocation

            if WINDOWS:
                p = Popen(
                    "cd %s & yotta --plain build" % buildLocation,
                    shell=True,
                    stderr=PIPE,
                    stdin=PIPE,
                    stdout=PIPE
                )
            else:
                p = Popen(
                    ["cd %s; yotta --plain build" % buildLocation],
                    shell=True,
                    stderr=PIPE,
                    stdin=PIPE,
                    stdout=PIPE,
                    close_fds = True
                )
            pipes = [p.stdin, NBSR(p.stdout, p), NBSR(p.stderr, p)]

    def startBuildAndUpload(self, *args):
        global mbedUploading
        global mbedBuilding
        global uBitUploading
        global uBitFound
        global pipes
        if not (mbedUploading or mbedBuilding):
            txtB = gtkSourceView.Buffer()
            txtB.set_style_scheme(self.style_scheme)
            txtB.set_highlight_matching_brackets(False)
            txtB.set_highlight_syntax(False)
            txtB.place_cursor(txtB.get_start_iter())

            self.consoleBody.props.buffer = txtB
            mbedBuilding = True
            mbedUploading = True
            self.clearBuild()
            for f in self.notebook:
                fn = self.notebook.get_tab_label(f).get_children()[0].get_label()
                tb = f.get_child().get_buffer()
                text = tb.get_text(*tb.get_bounds())
                open(os.path.join(buildLocation, "source/%s" %
                                  fn), 'w').write(text)

            os.chdir(buildLocation)
            os.environ["PWD"] = buildLocation

            if WINDOWS:
                p = Popen(
                    "cd %s & yotta --plain build" % buildLocation,
                    shell=True,
                    stderr=PIPE,
                    stdin=PIPE,
                    stdout=PIPE
                )
            else:
                p = Popen(
                    ["cd %s; yotta --plain build" % buildLocation],
                    shell=True,
                    stderr=PIPE,
                    stdin=PIPE,
                    stdout=PIPE,
                    close_fds = True
                )
            pipes = [p.stdin, NBSR(p.stdout, p), NBSR(p.stderr, p)]

    def importFile(self, *args):
        fn = gtk.FileChooserDialog(title="Import File",
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
        global mbedUploading
        global mbedBuilding
        global uBitUploading
        global uBitFound
        global pipes
        if os.path.exists("%s/build/bbc-microbit-classic-gcc/source/microbit-build-combined.hex" % buildLocation):
            if (not mbedBuilding) and (not mbedUploading):
                uBitUploading = True
                thread = Thread(target=upload, args=(self,))
                thread.daemon = True
                thread.start()

    def closePage(self, widget, *args):
        pn = self.notebook.page_num(widget)
        if self.ask("Are you sure you want to delete this file?\nThis action cannot be undone!"):
            self.notebook.remove_page(pn)
            if self.notebook.get_n_pages() == 0:
                self.addNotebookPage("main.cpp", '')

    def newPage(self, *args):
        pageName = self.askQ("File Name")
        if pageName:
            self.addNotebookPage(pageName, '')

    def getModified(self):
        return any([i.get_child().get_buffer().get_modified() for i in self.notebook])

    def setSaved(self):
        for i in self.notebook:
            i.get_child().props.buffer.set_modified(False)

    def showSettings(self, *args):
        sd=SettingsDialog()
        sd.run()
        sd.destroy()

    def main(self):
        thread = Thread(target=uBitPoller)
        thread.daemon = True
        thread.start()
        thread = Thread(target=pipePoller, args=(self,))
        thread.daemon = True
        thread.start()
        thread = Thread(target=updateTitle)
        thread.daemon = True
        thread.start()
        gtk.main()

