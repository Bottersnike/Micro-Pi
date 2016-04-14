try:
    import os
    import sys

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

    HOMEDIR = os.path.expanduser('~')

    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    if not os.path.exists(os.path.join(HOMEDIR, '.micropi')):
        os.mkdir(os.path.join(HOMEDIR, '.micropi'))

    defualtConfig = """darkHighlight: (50, 130, 50)
quickstart: %s
mbitLocation: "%s"
lightbgColour: (36, 36, 36)
theme: "darkgreen"
highlightColour: (73, 182, 73)
backgroundColour: (36, 36, 36)
fileExtention: "mpi\""""
    if not os.path.exists(os.path.join(HOMEDIR, '.micropi', 'config.conf')):
        try:
            import tkinter as tk
            import tkinter.messagebox as msgbox
            import tkinter.simpledialog as simpd
        except ImportError:
            import Tkinter as tk
            import tkMessageBox as msgbox
            import tkSimpleDialog as simpd
        root = tk.Tk()
        root.withdraw()
        res = msgbox.askyesno("Settings", "Enable Quick Start?")
        res2 = simpd.askstring("Settings", "Micro:Bit Location")
        if not res2:
            res2 = "/media/MICROBIT"
        root.destroy()
        print("Creating Config")
        open(os.path.join(HOMEDIR, '.micropi', 'config.conf'),
             'w').write(defualtConfig % (str(res), res2))
    configLocation = os.path.join(HOMEDIR, '.micropi', 'config.conf')

    if not os.path.exists(os.path.join(HOMEDIR, '.micropi', 'buildEnv')):
        print("Installing Build Enviroment")
        copyDir('buildEnv', os.path.join(HOMEDIR, '.micropi', 'buildEnv'))
    buildLocation = os.path.join(HOMEDIR, '.micropi', 'buildEnv')

    SETTINGS = {}
    d = open(configLocation).read().split('\n')
    for i in d:
        i2 = i.split(':')
        if i:
            SETTINGS[i[:len(i2[0])]] = eval(i[len(i2[0]) + 1:])

    import pygame
    import random
    import os
    import pygame.gfxdraw as gfx
    import sys
    import time
    try:
        import thread
    except:
        import _thread as thread
    import string
    import logging
    import pickle
    from threading import Thread
    try:
        from Queue import Queue, Empty
    except:
        from queue import Queue, Empty

    from subprocess import PIPE, Popen

    s = pygame.image.load('data/icon.png')
    pygame.display.set_icon(s)

    os.environ['SDL_VIDEO_CENTERED'] = 'true'
    f = os.listdir('data/splashScreens')
    _file = random.choice(f)
    img = pygame.image.load('data/splashScreens/%s' % _file)
    pygame.init()
    displaySettings = pygame.display.Info()
    screen = pygame.display.set_mode(img.get_size(), pygame.NOFRAME)
    screen.blit(img, (0, 0))
    pygame.display.flip()
    pygame.display.set_caption('Micro:Pi', 'Micro:Pi')

    t = time.localtime()
    val = '%d-%d-%d-%d' % (t.tm_hour, t.tm_wday, t.tm_mon, t.tm_year)
    LOGDIR = os.path.join(HOMEDIR, '.micropi', 'logs')
    if not os.path.exists(LOGDIR):
        os.mkdir(LOGDIR)
    logging.basicConfig(
        level=logging.DEBUG,
        filename="%s/%s.log" % (LOGDIR, val),
        format="[%(levelname)s][%(relativeCreated)d] %(message)s"
    )

    pipes = None

    fullscreen = False


    class NBSR:
        """
        A wrapper arround PIPES to make them easier to use
        """

        def __init__(self, stream):
            self._s = stream
            self._q = Queue()
            self._a = True

            def _populateQueue(stream, queue):
                while self._a:
                    line = stream.readline()
                    if line:
                        queue.put(line)
                    else:
                        self._a = False

            self._t = Thread(
                target=_populateQueue,
                args=(self._s, self._q)
            )
            self._t.daemon = True
            self._t.start()

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


    def askstring(prompt, command):
        global showTextDialog
        global textDialogPrompt
        global textDialogText
        global textDialogCursor
        global textDialogCommand
        showTextDialog = True
        textDialogPrompt = prompt
        textDialogText = ''
        textDialogCursor = 0
        textDialogCommand = command


    def askyesno(question, command):
        global showQuery
        global queryCommand
        global queryQuestion
        showQuery = True
        queryCommand = command
        queryQuestion = question


    def message(msg, icon="info"):
        global showMessage
        global messageContents
        showMessage = True
        messageContents = msg


    def split(string, sep):
        rtn = []
        curr = ''
        for i in string:
            curr += i
            if i == sep:
                rtn.append(curr)
                curr = ''
        if curr:
            rtn += curr
            curr = ''
        # rtn.append('')
        return rtn


    def save():
        if saveLoc:
            data = pickle.dump(files, open(saveLoc, 'w'))
        else:
            saveas()


    def saveas():
        global showFileCreate
        global fileCreateDir
        global fileCreateScrollY
        global fileCreateSelected
        global fileCreateFunc
        showFileCreate = True
        fileCreateDir = os.getcwd()
        fileCreateScrollY = 0
        fileCreateSelected = ''
        fileCreateFunc = create


    def saveFile(__file):
        global saveLoc
        _dir = fileCreateDir
        path = os.path.join(_dir, __file)
        if path[-4:] != '.%s' % SETTINGS["fileExtention"]:
            path += '.%s' % SETTINGS["fileExtention"]
        saveLoc = path
        save()


    def load(location=None):
        global files
        global saveLoc
        if location:
            try:
                saveLoc = location
                files = pickle.load(open(location, 'rb'))
            except KeyError:
                message(
                    "File does not apprear to be\na Micro:Pi save file",
                    "error"
                )


    def menuLoad():
        global showFileSelect
        global fileSelectDir
        global fileSelectFunc
        global fileSelectScrollY
        global fileSelectSelected
        showFileSelect = True
        fileSelectDir = os.getcwd()
        fileSelectScrollY = 0
        fileSelectSelected = ''
        fileSelectFunc = load


    def settings():
        global showSettings
        global settingsCursor
        global typinginSettings
        typinginSettings = False
        settingsCursor = 0
        showSettings = not showSettings
        saveConfig()


    def rstbuild():
        delFolder(os.path.join(buildLocation, 'build'))


    def quit():
        pygame.quit()
        sys.exit(0)


    def about():
        message(aboutMessage)


    def example(path):
        global files, saveLoc
        try:
            saveLoc = ''
            files = pickle.load(open('examples/%s' % path + '.%s' % SETTINGS["fileExtention"], 'rb'))
        except KeyError:
            message(
                "File does not apprear to be\na Micro:Pi save file",
                "error"
            )


    def importFile():
        global showFileSelect
        global fileSelectDir
        global fileSelectFunc
        global fileSelectScrollY
        global fileSelectSelected
        showFileSelect = True
        fileSelectDir = os.getcwd()
        fileSelectScrollY = 0
        fileSelectSelected = ''
        fileSelectFunc = addFile


    def addFile(path):
        d = open(path).read()
        files.append([path.split(os.path.sep)[-1], d])


    def newFile(name):
        files.append([name, '\n'])


    def create(null=None):
        pass


    def log(data):
        print(data)
        logging.debug(data)


    def delFolder(path):
        if os.path.exists(path):
            for i in os.listdir(path):
                if os.path.isdir(os.path.join(path, i)):
                    delFolder(os.path.join(path, i))
                    os.rmdir(os.path.join(path, i))
                else:
                    os.remove(os.path.join(path, i))


    def rstres():
        delFolder(os.path.join(buildLocation,
                               '/build/bbc-microbit-classic-gcc/source'))


    def startBuilding():
        global pipes
        for f in files:
            open(os.path.join(buildLocation, 'source/%s' % f[0]), 'w').write(f[1])

        prevLoc = os.getcwd()
        os.chdir(buildLocation)

        if WINDOWS:
            p = Popen(
                ['yotta', '--plain build'],
                shell=True,
                stderr=PIPE,
                stdin=PIPE,
                stdout=PIPE
            )
        else:
            p = Popen(
                ['yotta --plain build'],
                shell=True,
                stderr=PIPE,
                stdin=PIPE,
                stdout=PIPE
            )
        os.chdir(prevLoc)
        pipes = (p.stdin, NBSR(p.stdout), NBSR(p.stderr))


    def upload():
        end = open('%s/build/bbc-microbit-classic-gcc/source/\
microbit-combined.hex' % buildLocation).read()
        open(
            '%s/microbit-combined.hex' % SETTINGS['mbitLocation'],
            'w'
        ).write(end)


    def drawButon(surface, rect, colour, text, textCol):
        t = font2.render(text, 1, textCol)

        x, y, w, h = rect
        if w == 0:
            w = t.get_width()
        if h == 0:
            h = t.get_height()
        if y == 0:
            y = 105 - h

        s = h / 4
        s = int(round(s))

        gfx.aacircle(surface, x + s, y + s, s, colour)
        gfx.filled_circle(surface, x + s, y + s, s, colour)
        gfx.aacircle(surface, x + w - s, y + s, s, colour)
        gfx.filled_circle(surface, x + w - s, y + s, s, colour)
        gfx.aacircle(surface, x + s, y + h - s, s, colour)
        gfx.filled_circle(surface, x + s, y + h - s, s, colour)
        gfx.aacircle(surface, x + w - s, y + h - s, s, colour)
        gfx.filled_circle(surface, x + w - s, y + h - s, s, colour)

        drawRect(screen, colour, (x + s, y, w - 2 * s, h))
        drawRect(screen, colour, (x, y + s, w + 1, h - 2 * s))

        xo = (x + w / 2) - t.get_width() / 2
        yo = (y + h / 2) - t.get_height() / 2
        surface.blit(t, (xo, yo))

        return pygame.Rect(x, y, w, h)

    def drawCircle(screen, colour, p, r, w=0):
        x, y = p
        pygame.draw.circle(screen, colour, (int(x), int(y)), int(r), w)

    def drawRect(screen, colour, rect, w=0):
        r = (int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3]))
        pygame.draw.rect(screen, colour, r, w)

    def saveConfig():
        data = ''
        for i in SETTINGS.keys():
            p2 = str(SETTINGS[i])
            if type(SETTINGS[i]) == str or type(SETTINGS[i]) == type(u''):
                p2 = '"%s"' % p2
            data += '%s: %s\n' % (str(i), p2)
        open(configLocation, 'w').write(data)


    def delopenfile(n):
        global currFile
        files.remove(files[n])
        if n == len(fileRects) - 2 and n != 0:
            currFile -= 1
        elif len(files) == 0:
            files.append(['main.cpp', '\n'])

    log("Loading Fonts")

    font = pygame.font.Font('data/Monospace.ttf', 12)
    font2 = pygame.font.Font('data/Roboto.ttf', 24)
    font3 = pygame.font.Font('data/Roboto.ttf', 48)

    saveLoc = ""
    files = [["main.cpp", """#include "MicroBit.h"
#include "header.h"

void app_main()
{

}
"""], ["header.h", "\n"]]
    currFile = 0

    consoleText = ""
    aboutMessage = """Micro:Pi
An IDE built in pure python for developing
and deploying code to a BBC Micro:Mit

Made By Nathan Taylor
Thanks to lanchester university
for the microbit runtime.

Micro:Pi is not affiliated with the BBC in any way."""

    cursorPos = 0
    scrollY = 0
    cscrollY = 0

    pygame.key.set_repeat(250, 50)

    log("Loading Icons")

    consoleGreenIcon = pygame.image.load('data/icons/consoleGreen.png')
    consoleBlueIcon = pygame.image.load('data/icons/consoleBlue.png')
    consoleRedIcon = pygame.image.load('data/icons/consoleRed.png')
    consoleYellowIcon = pygame.image.load('data/icons/consoleYellow.png')

    menuGreenIcon = pygame.image.load('data/icons/menuGreen.png')
    menuBlueIcon = pygame.image.load('data/icons/menuBlue.png')
    menuRedIcon = pygame.image.load('data/icons/menuRed.png')
    menuYellowIcon = pygame.image.load('data/icons/menuYellow.png')

    uploadGreenIcon = pygame.image.load('data/icons/uploadGreen.png')
    uploadBlueIcon = pygame.image.load('data/icons/uploadBlue.png')
    uploadRedIcon = pygame.image.load('data/icons/uploadRed.png')
    uploadYellowIcon = pygame.image.load('data/icons/uploadYellow.png')

    uploadingIcon = pygame.image.load('data/icons/uploading.png')

    buildGreenIcon = pygame.image.load('data/icons/buildGreen.png')
    buildBlueIcon = pygame.image.load('data/icons/buildBlue.png')
    buildRedIcon = pygame.image.load('data/icons/buildRed.png')
    buildYellowIcon = pygame.image.load('data/icons/buildYellow.png')

    buildingIcon = pygame.image.load('data/icons/building.png')

    log("Generating Menus")

    exampleMenu = [(i[:-4] if i[-4:] == '.mpi' else i, example)
                   for i in os.listdir('examples')]
    menuData = [
        ('Save', save),
        ('Save As', saveas),
        ('Load', menuLoad),
        ('Import File', importFile),
        ('Examples', exampleMenu),
        ('', lambda:0), ('About', about),
        ('Settings', settings),
        ('Reset Build', rstbuild),
        ('', lambda:0),
        ('Exit', quit)]

    themes = {
        'darkgreen': [
            (73, 182, 73),
            (50, 130, 50),
            (36, 36, 36)
        ],
        'darkblue': [
            (72, 119, 182),
            (50, 83, 128),
            (36, 36, 36)
        ],
        'darkyellow': [
            (204, 193, 56),
            (166, 157, 46),
            (36, 36, 36)
        ],
        'darkred': [
            (182, 82, 73),
            (153, 69, 61),
            (36, 36, 36)
        ],
    }

    log("Setting Up Dialogs")

    cursor = True
    console = True
    menu = False
    showAbout = False
    showExampleMenu = False
    showSettings = False
    settingsRendered = False
    typinginSettings = False
    settingsCursor = 0
    showFileSelect = False
    fileSelectDir = os.getcwd()
    fileSelectScrollY = 0
    fileSelectSelected = ''
    fileSelectFunc = load
    showFileCreate = False
    fileCreateDir = os.getcwd()
    fileCreateScrollY = 0
    fileCreateSelected = ''
    fileCreateFunc = create
    showMessage = False
    messageContents = ''
    showQuery = False
    queryCommand = ''
    queryQuestion = ''
    queryRendered = False

    showTextDialog = False
    textDialogPrompt = ''
    textDialogText = ''
    textDialogCursor = 0
    textDialogCommand = ''

    mbitFound = False
    mbitUploading = False

    mbedBuilding = False
    mbedUploading = False

    fullScreenTick = 0
    fullScreenDelay = 100
    CLOCK = pygame.time.Clock()

    renderedChars = {}

    log("Prepering Yotta")

    if not SETTINGS['quickstart']:
        rstbuild()
    prevLoc = os.getcwd()
    os.chdir(buildLocation)
    os.system('yotta target bbc-microbit-classic-gcc')
    if not SETTINGS['quickstart']:
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
                ['yotta', 'build --plain'],
                shell=True,
                stderr=PIPE,
                stdin=PIPE,
                stdout=PIPE
            )
        else:
            p = Popen(
                ['yotta build --plain'],
                shell=True,
                stderr=PIPE,
                stdin=PIPE,
                stdout=PIPE
            )
        pipes = (p.stdin, NBSR(p.stdout), NBSR(p.stderr))

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
                log(d1[:-1])
                screen.blit(img, (0, 0))
                t = font.render(d1[:-1], 1, (73, 182, 73))
                screen.blit(t, (0, img.get_height() - t.get_height()))
            if d2:
                log(d2[:-1])
                screen.blit(img, (0, 0))
                t = font.render(d2[:-1], 1, (73, 182, 73))
                screen.blit(t, (0, img.get_height() - t.get_height()))
            pygame.display.flip()

            if not (pipes[1].alive()) or (not pipes[2].alive()):
                pipes = None
    os.chdir(prevLoc)

    log("Starting Micro:Pi")

    screen = pygame.display.set_mode((750, 500), pygame.RESIZABLE)
    screen_size = screen.get_size()
    pygame.display.set_caption('Micro:Pi', 'Micro:Pi')
    pygame.time.set_timer(29, 1000)

    os.environ.pop('SDL_VIDEO_CENTERED')

    while True:
        pygame.display.set_caption(
            "Micro:Pi - %s - %s" % (saveLoc, files[currFile][0]),
            "Micro:Pi - %s - %s" % (saveLoc, files[currFile][0])
        )
        settingsRendered = False
        filesRendered = False
        queryRendered = False
        fileCreateRendered = False
        textDialogRendered = False
        fileRects = []
        mbitFound = os.path.exists(SETTINGS['mbitLocation'])
        if not mbitFound and mbitUploading:
            mbitUploading = False
            mbedUploading = False

        if pipes:
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
                log(d1[:-1])
            if d2:
                log(d2[:-1])
            cw = screen_size[0] - 10
            cwcs = int(round(cw / font.size(' ')[0]))

            d1 = '\n'.join([d1[i:i + cwcs] for i in range(0, len(d1), cwcs)])
            d2 = '\n'.join([d2[i:i + cwcs] for i in range(0, len(d2), cwcs)])
            consoleText += d1 + d2

            if not (pipes[1].alive()) or (not pipes[2].alive()):
                pipes = None
                mbedBuilding = False
                if os.path.exists('%s/build/bbc-microbit-classic-gcc\
/source/microbit-combined.hex' % buildLocation):
                    consoleText += "Done!\n"
                    if mbedUploading and mbitFound:
                        consoleText += "Uploading!\n"
                        mbitUploading = True
                        thread.start_new_thread(upload, ())
                    elif mbedUploading:
                        mbitUploading = False
                        mbedUploading = False
                        consoleText += """Cannot upload!
Micro:Bit not found!
Check it is plugged in and Micro:Pi knows where to find it."""
                else:
                    consoleText += "An error has occured\n"
                    consoleText += "It is advised to look back to the last\
line of compiling to find the error!\n"
                    message("""There is an error
with your code!
It is advised to scroll
back through the console
to find out what the error is!""", "error")
                    mbitUploading = False
                    mbedUploading = False

        if console:
            textBottom = screen_size[1] / 3 * 2
        else:
            textBottom = screen_size[1] - 5

        screen.fill(SETTINGS['backgroundColour'])

        if not mbitFound:
            col = (182, 73, 73)
        elif mbitUploading:
            col = (182, 135, 73)
        else:
            col = SETTINGS['highlightColour']

        gfx.aapolygon(screen, [(0, 0), (0, 100), (100, 0)], col)
        gfx.filled_polygon(screen, [(0, 0), (0, 100), (100, 0)], col)

        gfx.aapolygon(screen, [(100, 0), (100, 75), (175, 0)], col)
        gfx.filled_polygon(screen, [(100, 0), (100, 75), (175, 0)], col)

        gfx.aapolygon(screen, [(175, 0), (175, 50), (225, 0)], col)
        gfx.filled_polygon(screen, [(175, 0), (175, 50), (225, 0)], col)

        gfx.aapolygon(screen, [(225, 0), (225, 25), (250, 0)], col)
        gfx.filled_polygon(screen, [(225, 0), (225, 25), (250, 0)], col)

        x = 50
        f2 = []
        for f in files:
            f2.append(f[0] + ' x')
        for n, f in enumerate(f2 + [' + ']):
            if n != currFile:
                rect = drawButon(
                    screen,
                    (x, 0, 0, 0),
                    SETTINGS['highlightColour'],
                    f,
                    (20, 20, 20)
                )
            else:
                rect = drawButon(
                    screen,
                    (x, 0, 0, 0),
                    SETTINGS['darkHighlight'],
                    f,
                    (20, 20, 20)
                )
            x += rect.w + 5
            fileRects.append(rect)

        lines = len(files[currFile][1].split('\n'))
        digits = len(str(lines - 1))
        hs = font.size('0')[0]
        sp = hs * digits + 5
        drawRect(
            screen,
            (219, 219, 219),
            (5, 105, screen_size[0] - 10, textBottom - 105)
        )
        drawRect(
            screen,
            (182, 182, 182),
            (5, 105, sp, textBottom - 105)
        )

        y = 105 + scrollY
        p = 0
        for n, line in enumerate(files[currFile][1].split('\n')):
            if y < textBottom and y >= 100:
                if str(n) not in renderedChars:
                    ln = font.render(str(n), 1, (36, 36, 36))
                    renderedChars[str(n)] = ln
                else:
                    ln = renderedChars[str(n)]
                screen.blit(ln, (5, y))
                t = font.render(line, 1, SETTINGS['backgroundColour'])

                x = sp + 5
                for cn, c in enumerate(line + ' '):
                    if c == '	':
                        c = '    '
                    if cursor and p == cursorPos:
                        pygame.draw.line(
                            screen,
                            (36, 36, 36),
                            (x, y),
                            (x, y + t.get_height())
                        )
                    if c not in renderedChars:
                        t = font.render(c, 1, (36, 36, 36))
                        renderedChars[c] = t
                    else:
                        t = renderedChars[c]
                    screen.blit(t, (x, y))
                    x += t.get_width()
                    p += 1
            else:
                for cn, c in enumerate(line + ' '):
                    p += 1

            y += font.get_height()

        if console:
            drawRect(
                screen,
                (230, 230, 230),
                (5,
                 textBottom + 5,
                 screen_size[0] - 10,
                 screen_size[1] - 10 - textBottom
                 )
            )
            x = 5
            y = textBottom + 5 + cscrollY
            for line in consoleText.split('\n'):
                if y < screen_size[1] - 5 and y > textBottom:
                    t = font.render(line, 1, (36, 36, 36))
                    screen.blit(t, (x, y))
                y += font.get_height()

        if SETTINGS['theme'] == 'darkgreen':
            screen.blit(menuGreenIcon, (screen_size[0] - 52, 2))
            screen.blit(consoleGreenIcon, (screen_size[0] - 105, 2))
            screen.blit(buildGreenIcon if not mbedBuilding else buildingIcon,
                        (screen_size[0] - 211, 2))
            screen.blit(uploadGreenIcon if not mbedUploading else uploadingIcon,
                        (screen_size[0] - 158, 2))
        elif SETTINGS['theme'] == 'darkred':
            screen.blit(menuRedIcon, (screen_size[0] - 52, 2))
            screen.blit(consoleRedIcon, (screen_size[0] - 105, 2))
            screen.blit(buildRedIcon if not mbedBuilding else buildingIcon,
                        (screen_size[0] - 211, 2))
            screen.blit(uploadRedIcon if not mbedUploading else uploadingIcon,
                        (screen_size[0] - 158, 2))
        elif SETTINGS['theme'] == 'darkyellow':
            screen.blit(menuYellowIcon, (screen_size[0] - 52, 2))
            screen.blit(consoleYellowIcon, (screen_size[0] - 105, 2))
            screen.blit(buildYellowIcon if not mbedBuilding else buildingIcon,
                        (screen_size[0] - 211, 2))
            screen.blit(uploadYellowIcon if not mbedUploading else uploadingIcon,
                        (screen_size[0] - 158, 2))
        elif SETTINGS['theme'] == 'darkblue':
            screen.blit(menuBlueIcon, (screen_size[0] - 52, 2))
            screen.blit(consoleBlueIcon, (screen_size[0] - 105, 2))
            screen.blit(buildBlueIcon if not mbedBuilding else buildingIcon,
                        (screen_size[0] - 211, 2))
            screen.blit(uploadBlueIcon if not mbedUploading else uploadingIcon,
                        (screen_size[0] - 158, 2))

        f = lambda x: font2.size(x[0])[0]
        menuWidth = font2.size(max(menuData, key=f)[0])[0] * 2
        menuHeight = len(menuData) * font2.get_height()
        menuRect = pygame.Rect(
            screen_size[0] - menuWidth,
            55,
            menuWidth,
            menuHeight
        )

        if showSettings:
            settingsRendered = True
            settingsRect = pygame.Rect(0, 0, 300, 400)
            settingsRect.x = screen_size[0] / 2 - settingsRect.w / 2
            settingsRect.y = screen_size[1] / 2 - settingsRect.h / 2
            drawRect(screen, (20, 20, 20), settingsRect)
            border = 2
            settingsRect.x += border
            settingsRect.y += border
            settingsRect.w -= border * 2
            settingsRect.h -= border * 2
            drawRect(
                screen,
                SETTINGS['backgroundColour'],
                settingsRect
            )
            x, y = settingsRect.x, settingsRect.y
            t = font3.render("Settings", 1, SETTINGS['highlightColour'])
            screen.blit(t, (x, y + font3.get_descent()))
            y += t.get_height()

            t = font2.render("Quick Start", 1, SETTINGS['highlightColour'])
            screen.blit(t, (x, y))
            quickStartRect = pygame.Rect(
                x + t.get_width() + t.get_height() / 2,
                y + t.get_height() / 4,
                t.get_height() / 2,
                t.get_height() / 2
            )
            drawRect(
                screen,
                SETTINGS['highlightColour'],
                quickStartRect,
                0 if SETTINGS['quickstart'] else 1
            )
            y += t.get_height()

            t = font2.render(
                "Micro:Bit Location:",
                1,
                SETTINGS['highlightColour']
            )
            screen.blit(t, (x, y))
            y += t.get_height()
            textInputRect = pygame.Rect(
                x + 2,
                y,
                settingsRect.w - 4,
                t.get_height() + 4
            )
            drawRect(screen, (20, 20, 20), textInputRect)
            textInputRect.x += border
            textInputRect.y += border
            textInputRect.w -= border * 2
            textInputRect.h -= border * 2
            drawRect(screen, (170, 170, 170), textInputRect)

            xx = textInputRect.x
            for n, i in enumerate(SETTINGS['mbitLocation']):
                t = font2.render(i, 1, SETTINGS['backgroundColour'])
                screen.blit(t, (xx, textInputRect.y))
                if n == settingsCursor and typinginSettings:
                    pygame.draw.line(
                        screen,
                        SETTINGS['backgroundColour'],
                        (
                            xx,
                            textInputRect.y
                        ),
                        (
                            xx,
                            textInputRect.y + textInputRect.h
                        )
                    )
                xx += t.get_width()
            if settingsCursor >= len(SETTINGS['mbitLocation']) and typinginSettings:
                pygame.draw.line(
                    screen,
                    SETTINGS['backgroundColour'],
                    (
                        xx,
                        textInputRect.y
                    ),
                    (
                        xx,
                        textInputRect.y + textInputRect.h
                    )
                )
            y += textInputRect.h

            t = font2.render("Theme:", 1, SETTINGS['highlightColour'])
            screen.blit(t, (x, y))
            y += t.get_height()

            drawCircle(
                screen,
                SETTINGS['highlightColour'],
                (
                    x + t.get_height() / 2,
                    y + t.get_height() / 2
                ),
                t.get_height() / 4,
                0 if SETTINGS['theme'] == 'darkgreen' else 1
            )
            darkGreenRect = pygame.Rect(
                x + t.get_height() / 4,
                y + t.get_height() / 4,
                t.get_height() / 2,
                t.get_height() / 2
            )
            t = font2.render("Dark Green", 1, SETTINGS['highlightColour'])
            screen.blit(t, (x + t.get_height(), y))
            y += t.get_height()

            drawCircle(
                screen,
                SETTINGS['highlightColour'],
                (
                    x + t.get_height() / 2,
                    y + t.get_height() / 2
                ),
                t.get_height() / 4,
                0 if SETTINGS['theme'] == 'darkblue' else 1
            )
            darkBlueRect = pygame.Rect(
                x + t.get_height() / 4,
                y + t.get_height() / 4,
                t.get_height() / 2,
                t.get_height() / 2
            )
            t = font2.render("Dark Blue", 1, SETTINGS['highlightColour'])
            screen.blit(t, (x + t.get_height(), y))
            y += t.get_height()

            drawCircle(
                screen,
                SETTINGS['highlightColour'],
                (
                    x + t.get_height() / 2,
                    y + t.get_height() / 2
                ),
                t.get_height() / 4,
                0 if SETTINGS['theme'] == 'darkyellow' else 1
            )
            darkYellowRect = pygame.Rect(
                x + t.get_height() / 4,
                y + t.get_height() / 4,
                t.get_height() / 2,
                t.get_height() / 2
            )
            t = font2.render("Dark Yellow", 1, SETTINGS['highlightColour'])
            screen.blit(t, (x + t.get_height(), y))
            y += t.get_height()

            drawCircle(
                screen,
                SETTINGS['highlightColour'],
                (
                    x + t.get_height() / 2,
                    y + t.get_height() / 2
                ),
                t.get_height() / 4,
                0 if SETTINGS['theme'] == 'darkred' else 1
            )
            darkRedRect = pygame.Rect(
                x + t.get_height() / 4,
                y + t.get_height() / 4,
                t.get_height() / 2,
                t.get_height() / 2
            )
            t = font2.render("Dark Red", 1, SETTINGS['highlightColour'])
            screen.blit(t, (x + t.get_height(), y))
            y += t.get_height()
        if showFileSelect:
            filesRendered = True
            fileSelectRect = pygame.Rect(0, 0, 500, 300)
            fileSelectRect.x = screen_size[0] / 2 - fileSelectRect.w / 2
            fileSelectRect.y = screen_size[1] / 2 - fileSelectRect.h / 2
            drawRect(screen, (20, 20, 20), fileSelectRect)
            border = 2
            fileSelectRect.x += border
            fileSelectRect.y += border
            fileSelectRect.w -= border * 2
            fileSelectRect.h -= border * 2
            drawRect(
                screen,
                SETTINGS['backgroundColour'],
                fileSelectRect
            )
            x, y = fileSelectRect.x, fileSelectRect.y

            t3 = font3.render(
                "Select A File",
                1,
                SETTINGS['highlightColour']
            )
            screen.blit(t3, (x, y + font3.get_descent()))
            y += t3.get_height()

            t = font2.render("Back", 1, SETTINGS['highlightColour'])
            fsBackRect = pygame.Rect(
                fileSelectRect.x + (fileSelectRect.w -
                                    t.get_width()) - border * 3,
                fileSelectRect.y + (fileSelectRect.h -
                                    t.get_height()) - border * 3,
                t.get_width() + border * 2,
                t.get_height() + border * 2)
            drawRect(screen, (20, 20, 20), fsBackRect)
            fsBackRect.x += border
            fsBackRect.y += border
            fsBackRect.w -= border * 2
            fsBackRect.h -= border * 2
            drawRect(
                screen,
                SETTINGS['backgroundColour'],
                fsBackRect
            )
            screen.blit(t, fsBackRect)

            t2 = font2.render("Open", 1, SETTINGS['highlightColour'])
            fsOpenRect = pygame.Rect(
                fileSelectRect.x + (fileSelectRect.w -
                                    t2.get_width()) - border * 6 -
                t.get_width(),
                fileSelectRect.y + (fileSelectRect.h -
                                    t2.get_height()) - border * 3,
                t2.get_width() + border * 2,
                t2.get_height() + border * 2
            )
            drawRect(screen, (20, 20, 20), fsOpenRect)
            fsOpenRect.x += border
            fsOpenRect.y += border
            fsOpenRect.w -= border * 2
            fsOpenRect.h -= border * 2
            drawRect(
                screen,
                SETTINGS['backgroundColour'],
                fsOpenRect
            )
            screen.blit(t2, fsOpenRect)

            filesRect = pygame.Rect(
                x + border,
                y + font3.get_descent(),
                fileSelectRect.w - border * 2,
                fileSelectRect.h - t3.get_height() -
                t2.get_height()
            )
            drawRect(screen, (127, 127, 127), filesRect)
            filesRect.x += border
            filesRect.y += border
            filesRect.w -= border * 2
            filesRect.h -= border * 2
            drawRect(screen, (200, 200, 200), filesRect)

            fileSurf = pygame.Surface((filesRect.w, filesRect.h))
            fsy = 0
            fileSurf.fill((200, 200, 200))
            dirs = os.listdir(fileSelectDir)
            dirs.sort()
            for _file in ['..'] + dirs:
                if _file[0] != '.' or _file[:2] == '..':
                    if os.path.isdir(os.path.join(fileSelectDir, _file)):
                        _file = _file + os.path.sep
                    t = font.render(_file, 1, (36, 36, 36))
                    if _file == fileSelectSelected:
                        drawRect(
                            fileSurf,
                            (36, 36, 36),
                            (
                                0,
                                fsy + fileSelectScrollY,
                                fileSurf.get_width(),
                                t.get_height()
                            )
                        )
                        t = font.render(_file, 1, (200, 200, 200))
                    fileSurf.blit(t, (0, fsy + fileSelectScrollY))
                    fsy += t.get_height()
            if fsy > filesRect.h:
                sbw = 15
                drawRect(
                    fileSurf,
                    (20, 20, 20),
                    (filesRect.w - sbw, 0, sbw, filesRect.h)
                )
                drawRect(
                    fileSurf,
                    (200, 200, 200),
                    (
                        filesRect.w - sbw + 1,
                        1,
                        sbw - 2,
                        filesRect.h - 2
                    )
                )
                sbh = int(round(float(fsy) / filesRect.h))

                k = float(filesRect.y) / (fsy - 26 * 15)
                sby = abs(k * fileSelectScrollY) + 1

                drawRect(
                    fileSurf,
                    (120, 120, 120),
                    (filesRect.w - sbw + 1, sby, sbw - 2, sbh)
                )
            screen.blit(fileSurf, filesRect)
        if showFileCreate:
            fileCreateRendered = True
            fileCreateRect = pygame.Rect(0, 0, 500, 300)
            fileCreateRect.x = screen_size[0] / 2 - fileCreateRect.w / 2
            fileCreateRect.y = screen_size[1] / 2 - fileCreateRect.h / 2
            drawRect(screen, (20, 20, 20), fileCreateRect)
            border = 2
            fileCreateRect.x += border
            fileCreateRect.y += border
            fileCreateRect.w -= border * 2
            fileCreateRect.h -= border * 2
            drawRect(
                screen,
                SETTINGS['backgroundColour'],
                fileCreateRect
            )
            x, y = fileCreateRect.x, fileCreateRect.y

            t3 = font3.render(
                "Select A Location",
                1,
                SETTINGS['highlightColour']
            )
            screen.blit(t3, (x, y + font3.get_descent()))
            y += t3.get_height()

            t = font2.render("Back", 1, SETTINGS['highlightColour'])
            fcBackRect = pygame.Rect(
                fileCreateRect.x + (fileCreateRect.w -
                                    t.get_width()) - border * 3,
                fileCreateRect.y + (fileCreateRect.h -
                                    t.get_height()) - border * 3,
                t.get_width() + border * 2,
                t.get_height() + border * 2
            )
            drawRect(screen, (20, 20, 20), fcBackRect)
            fcBackRect.x += border
            fcBackRect.y += border
            fcBackRect.w -= border * 2
            fcBackRect.h -= border * 2
            drawRect(
                screen,
                SETTINGS['backgroundColour'],
                fcBackRect
            )
            screen.blit(t, fcBackRect)

            t2 = font2.render("Open", 1, SETTINGS['highlightColour'])
            fcOpenRect = pygame.Rect(
                fileCreateRect.x + (fileCreateRect.w -
                                    t2.get_width()) - border * 6 -
                t.get_width(),
                fileCreateRect.y + (fileCreateRect.h -
                                    t2.get_height()) - border * 3,
                t2.get_width() + border * 2,
                t2.get_height() + border * 2
            )
            drawRect(screen, (20, 20, 20), fcOpenRect)
            fcOpenRect.x += border
            fcOpenRect.y += border
            fcOpenRect.w -= border * 2
            fcOpenRect.h -= border * 2
            drawRect(
                screen,
                SETTINGS['backgroundColour'],
                fcOpenRect
            )
            screen.blit(t2, fcOpenRect)

            t4 = font2.render("Select", 1, SETTINGS['highlightColour'])
            fcSelectRect = pygame.Rect(
                fileCreateRect.x +
                (fileCreateRect.w -
                 t4.get_width()) - border * 9 -
                t.get_width() - t2.get_width(),
                fileCreateRect.y +
                (fileCreateRect.h -
                 t4.get_height()) - border * 3,
                t4.get_width() + border * 2,
                t4.get_height() + border * 2
            )
            drawRect(screen, (20, 20, 20), fcSelectRect)
            fcSelectRect.x += border
            fcSelectRect.y += border
            fcSelectRect.w -= border * 2
            fcSelectRect.h -= border * 2
            drawRect(
                screen,
                SETTINGS['backgroundColour'],
                fcSelectRect
            )
            screen.blit(t4, fcSelectRect)

            filescerRect = pygame.Rect(
                x + border,
                y + font3.get_descent(),
                fileCreateRect.w - border * 2,
                fileCreateRect.h - t2.get_height() -
                t3.get_height()
            )
            drawRect(screen, (127, 127, 127), filescerRect)
            filescerRect.x += border
            filescerRect.y += border
            filescerRect.w -= border * 2
            filescerRect.h -= border * 2
            drawRect(screen, (200, 200, 200), filescerRect)

            fileSurf = pygame.Surface((filescerRect.w, filescerRect.h))
            fcy = 0
            fileSurf.fill((200, 200, 200))
            dirs = os.listdir(fileCreateDir)
            dirs.sort()
            for _file in ['..'] + dirs:
                if _file[0] != '.' or _file[:2] == '..':
                    if os.path.isdir(os.path.join(fileCreateDir, _file)):
                        _file = _file + os.path.sep
                    t = font.render(_file, 1, (36, 36, 36))
                    if _file == fileCreateSelected:
                        drawRect(
                            fileSurf,
                            (36, 36, 36),
                            (
                                0,
                                fcy + fileCreateScrollY,
                                fileSurf.get_width(),
                                t.get_height()
                            )
                        )
                        t = font.render(_file, 1, (200, 200, 200))
                    fileSurf.blit(t, (0, fcy + fileCreateScrollY))
                    fcy += t.get_height()
            if fcy > filescerRect.h:
                sbw = 15
                drawRect(
                    fileSurf,
                    (20, 20, 20),
                    (
                        filescerRect.w - sbw,
                        0,
                        sbw,
                        filescerRect.h
                    )
                )
                drawRect(
                    fileSurf,
                    (200, 200, 200),
                    (
                        filescerRect.w - sbw + 1,
                        1,
                        sbw - 2,
                        filescerRect.h - 2
                    )
                )
                sbh = int(round(float(fcy) / filescerRect.h))

                k = float(filescerRect.y) / (fcy - 26 * 15)
                sby = abs(k * fileCreateScrollY) + 1

                drawRect(
                    fileSurf,
                    (120, 120, 120),
                    (
                        filescerRect.w - sbw + 1,
                        sby,
                        sbw - 2,
                        sbh
                    )
                )
            screen.blit(fileSurf, filescerRect)
        if showMessage:
            f2 = lambda x: font2.size(x)[0]
            border = 2
            m = messageContents.split('\n')
            w = font2.size(max(m, key=f2))[0]
            h = font2.size(m[0])[1] * (len(m) + 1) + border * 4
            x = (screen_size[0] - w) / 2
            y = (screen_size[1] - h) / 2
            messageRect = pygame.Rect(
                x - border,
                y - border,
                w + border * 2,
                h + border * 2
            )
            drawRect(screen, (20, 20, 20), messageRect)
            messageRect.x += border
            messageRect.y += border
            messageRect.w -= border * 2
            messageRect.h -= border * 2
            drawRect(screen, (36, 36, 36), messageRect)
            for line in m:
                t = font2.render(line, 1, SETTINGS['highlightColour'])
                screen.blit(t, ((screen_size[0] - t.get_width()) / 2, y))
                y += t.get_height()
            t = font2.render("Dismiss", 1, SETTINGS['highlightColour'])
            messageButtonRect = pygame.Rect(
                0,
                y + border,
                t.get_width() + border * 2,
                t.get_height() + border * 2
            )
            messageButtonRect.x = (screen_size[0] - messageButtonRect.w) / 2
            drawRect(screen, (20, 20, 20), messageButtonRect)
            messageButtonRect.x += border
            messageButtonRect.y += border
            messageButtonRect.w -= border * 2
            messageButtonRect.h -= border * 2
            drawRect(screen, (36, 36, 36), messageButtonRect)
            screen.blit(t, messageButtonRect)
        if showQuery:
            queryRendered = True
            border = 2
            w = max([
                font2.size(queryQuestion)[0],
                font2.size("Yes")[0] + font2.size("No")[0] +
                border * 7]) + border * 2
            h = font2.size(queryQuestion)[1] * 2 + border * 5
            queryRect = pygame.Rect(
                (screen_size[0] - w) / 2,
                (screen_size[
                    1] - h) / 2,
                w,
                h
            )
            drawRect(screen, (20, 20, 20), queryRect)
            queryRect.x += border
            queryRect.y += border
            queryRect.w -= border * 2
            queryRect.h -= border * 2
            drawRect(screen, (36, 36, 36), queryRect)
            y = queryRect.y
            t = font2.render(queryQuestion, 1, SETTINGS['highlightColour'])
            screen.blit(t, ((screen_size[0] - t.get_width()) / 2, y))
            y += t.get_height()
            yes = font2.render("Yes", 1, SETTINGS['highlightColour'])
            no = font2.render("No", 1, SETTINGS['highlightColour'])
            surf = pygame.Surface(
                (
                    font2.size("Yes")[0] +
                    font2.size("No")[0] + border * 5,
                    font2.size('Yes')[
                        1] + border * 2
                )
            )
            surf.fill((36, 36, 36))

            queryYesRect = pygame.Rect(
                queryRect.x + border,
                y,
                yes.get_width() + border * 2,
                yes.get_height() + border * 2
            )
            drawRect(screen, (20, 20, 20), queryYesRect)
            queryYesRect.x += border
            queryYesRect.y += border
            queryYesRect.w -= border * 2
            queryYesRect.h -= border * 2
            drawRect(screen, (36, 36, 36), queryYesRect)
            screen.blit(yes, queryYesRect)

            queryNoRect = pygame.Rect(
                queryRect.x + queryRect.w -
                no.get_width() - border * 3,
                y,
                no.get_width() + border * 2,
                no.get_height() + border * 2
            )
            drawRect(screen, (20, 20, 20), queryNoRect)
            queryNoRect.x += border
            queryNoRect.y += border
            queryNoRect.w -= border * 2
            queryNoRect.h -= border * 2
            drawRect(screen, (36, 36, 36), queryNoRect)
            screen.blit(no, queryNoRect)
        if showTextDialog:
            textDialogRendered = True
            border = 2
            w = max([font2.size(textDialogPrompt)[0], 500]) + border * 2
            h = font2.size(textDialogPrompt)[1] * 3 + border * 8
            textDialogRect = pygame.Rect(
                (screen_size[0] - w) / 2,
                (screen_size[
                    1] - h) / 2,
                w,
                h
            )
            drawRect(screen, (20, 20, 20), textDialogRect)
            textDialogRect.x += border
            textDialogRect.y += border
            textDialogRect.w -= border * 2
            textDialogRect.h -= border * 2
            drawRect(screen, (36, 36, 36), textDialogRect)
            y = textDialogRect.y

            t = font2.render(
                textDialogPrompt,
                1,
                SETTINGS['highlightColour']
            )
            screen.blit(t, ((screen_size[0] - t.get_width()) / 2, y))
            y += t.get_height()
            okay = font2.render("Okay", 1, SETTINGS['highlightColour'])
            cancel = font2.render("Cancel", 1, SETTINGS['highlightColour'])

            textDialogInputRect = pygame.Rect(
                textDialogRect.x + border,
                y,
                textDialogRect.w - border * 2,
                font2.size('SomeText')[1] +
                border * 2
            )
            drawRect(screen, (20, 20, 20), textDialogInputRect)
            textDialogInputRect.x += border
            textDialogInputRect.y += border
            textDialogInputRect.w -= border * 2
            textDialogInputRect.h -= border * 2
            drawRect(screen, (200, 200, 200), textDialogInputRect)

            x = textDialogInputRect.x
            for n, c in enumerate(textDialogText):
                t = font2.render(c, 1, (36, 36, 36))
                screen.blit(t, (x, textDialogInputRect.y))

                if n == textDialogCursor:
                    pygame.draw.line(
                        screen,
                        SETTINGS['backgroundColour'],
                        (
                            x,
                            textDialogInputRect.y
                        ),
                        (
                            x,
                            textDialogInputRect.y +
                            textDialogInputRect.h
                        )
                    )
                x += t.get_width()
            if textDialogCursor >= len(textDialogText):
                pygame.draw.line(
                    screen,
                    SETTINGS['backgroundColour'],
                    (
                        x,
                        textDialogInputRect.y
                    ),
                    (
                        x,
                        textDialogInputRect.y +
                        textDialogInputRect.h
                    )
                )
            y += t.get_height() + border * 3

            textDialogOkayRect = pygame.Rect(
                textDialogRect.x + border,
                y,
                okay.get_width() + border * 2,
                okay.get_height() + border * 2
            )
            drawRect(screen, (20, 20, 20), textDialogOkayRect)
            textDialogOkayRect.x += border
            textDialogOkayRect.y += border
            textDialogOkayRect.w -= border * 2
            textDialogOkayRect.h -= border * 2
            drawRect(screen, (36, 36, 36), textDialogOkayRect)
            screen.blit(okay, textDialogOkayRect)

            textDialogCancelRect = pygame.Rect(
                textDialogRect.x +
                textDialogRect.w -
                cancel.get_width() -
                border * 3,
                y,
                cancel.get_width() +
                border * 2,
                cancel.get_height() +
                border * 2
            )
            drawRect(screen, (20, 20, 20), textDialogCancelRect)
            textDialogCancelRect.x += border
            textDialogCancelRect.y += border
            textDialogCancelRect.w -= border * 2
            textDialogCancelRect.h -= border * 2
            drawRect(screen, (36, 36, 36), textDialogCancelRect)
            screen.blit(cancel, textDialogCancelRect)

        mp = pygame.mouse.get_pos()
        if menu:
            drawRect(screen, (230, 230, 230), menuRect)
            y = menuRect.y
            showExampleMenu = False
            for mi in menuData:
                mt = font2.render(mi[0], 1, SETTINGS['backgroundColour'])
                mr = mt.get_rect()
                mr.x = menuRect.x
                mr.y = y
                mr.w = menuWidth
                if mi[0] == "Examples":
                    exampleY = mr.y
                    emenuWidth = font2.size(max(exampleMenu, key=f)[0])[0] * 2
                    emenuHeight = len(exampleMenu) * font2.get_height()
                    emenuRect = pygame.Rect(
                        screen_size[0] - menuWidth -
                        emenuWidth,
                        exampleY,
                        emenuWidth,
                        emenuHeight
                    )
                    if emenuRect.collidepoint(mp):
                        showExampleMenu = True
                if mr.collidepoint(mp) and mi[0]:
                    if mi[0] == "Examples":
                        showExampleMenu = True
                    mr2 = pygame.Rect(mr)
                    mr2.x += 1
                    mr2.y += 1
                    mr2.w -= 2
                    mr2.h -= 2
                    drawRect(screen, (210, 210, 210), mr2)
                screen.blit(mt, mr)
                y += font2.get_height()
            if showExampleMenu:
                drawRect(screen, (230, 230, 230), emenuRect)
                y = exampleY
                for mi in exampleMenu:
                    mt = font2.render(
                        mi[0],
                        1,
                        SETTINGS['backgroundColour']
                    )
                    mr = mt.get_rect()
                    mr.x = emenuRect.x
                    mr.y = y
                    mr.w = emenuWidth
                    if mr.collidepoint(mp) and mi[0]:
                        mr2 = pygame.Rect(mr)
                        mr2.x += 1
                        mr2.y += 1
                        mr2.w -= 2
                        mr2.h -= 2
                        drawRect(screen, (210, 210, 210), mr2)
                    screen.blit(mt, mr)
                    y += font2.get_height()

        t = font.render(str(int(round(CLOCK.get_fps(), 0))) + "FPS", 1, (36, 36, 36))
        screen.blit(t, (0, 0))
        pygame.display.flip()
        CLOCK.tick()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if not showSettings and not showFileSelect and not showMessage and not showQuery and not showFileCreate and not showTextDialog:
                    if event.key == pygame.K_RIGHT:
                        cursor = True
                        if cursorPos < len(files[currFile][1]):
                            cursorPos += 1
                    elif event.key == pygame.K_LEFT:
                        cursor = True
                        if cursorPos > 0:
                            cursorPos -= 1
                    elif event.key == pygame.K_UP:
                        cursor = True
                        #cursorPos -= 1

                        y = 105 + scrollY
                        p = 0
                        p2 = cursorPos
                        cx = cy = 0
                        for n, line in enumerate(files[currFile][1].split('\n')):
                            if y < textBottom and y >= 100:

                                x = sp + 5
                                for cn, c in enumerate(line + ' '):
                                    if c == '	':
                                        c = '    '
                                    if cursor and p == cursorPos:
                                        cy = n
                                        cx = p2
                                    if c not in renderedChars:
                                        t = font.render(
                                            c,
                                            1,
                                            SETTINGS['backgroundColour']
                                        )
                                        renderedChars[c] = t
                                    else:
                                        t = renderedChars[c]
                                    screen.blit(t, (x, y))
                                    x += t.get_width()
                                    p += 1
                                p2 -= len(line) + 1

                            y += font.get_height()
                        if cy > 0:
                            cy -= 1

                            y = 105 + scrollY
                            p = 0
                            p2 = cursorPos
                            for n, line in enumerate(files[currFile][1].split('\n')):
                                if y < textBottom and y >= 100:

                                    x = sp + 5
                                    for cn, c in enumerate(line + ' '):
                                        if c == '	':
                                            c = '    '
                                        if cy == n:
                                            if cx > len(line):
                                                cx = len(line)
                                            if cx == cn:
                                                cursorPos = p
                                        if c not in renderedChars:
                                            t = font.render(
                                                c, 1, SETTINGS['backgroundColour'])
                                            renderedChars[c] = t
                                        else:
                                            t = renderedChars[c]
                                        screen.blit(t, (x, y))
                                        x += t.get_width()
                                        p += 1
                                    p2 -= len(line) + 1

                                y += font.get_height()
                    elif event.key == pygame.K_DOWN:
                        cursor = True
                        #cursorPos += 1

                        y = 105 + scrollY
                        p = 0
                        p2 = cursorPos
                        cx = cy = 0
                        for n, line in enumerate(files[currFile][1].split('\n')):
                            if y < textBottom and y >= 100:

                                x = sp + 5
                                for cn, c in enumerate(line + ' '):
                                    if c == '	':
                                        c = '    '
                                    if cursor and p == cursorPos:
                                        cy = n
                                        cx = p2
                                    if c not in renderedChars:
                                        t = font.render(
                                            c, 1, SETTINGS['backgroundColour'])
                                        renderedChars[c] = t
                                    else:
                                        t = renderedChars[c]
                                    screen.blit(t, (x, y))
                                    x += t.get_width()
                                    p += 1
                                p2 -= len(line) + 1

                            y += font.get_height()
                        if cy < len(files[currFile][1].split('\n')):
                            cy += 1

                            y = 105 + scrollY
                            p = 0
                            p2 = cursorPos
                            for n, line in enumerate(files[currFile][1].split('\n')):
                                if y < textBottom and y >= 100:

                                    x = sp + 5
                                    for cn, c in enumerate(line + ' '):
                                        if c == '	':
                                            c = '    '
                                        if cy == n:
                                            if cx > len(line):
                                                cx = len(line)
                                            if cx == cn:
                                                cursorPos = p
                                        if c not in renderedChars:
                                            t = font.render(
                                                c, 1, SETTINGS['backgroundColour'])
                                            renderedChars[c] = t
                                        else:
                                            t = renderedChars[c]
                                        screen.blit(t, (x, y))
                                        x += t.get_width()
                                        p += 1
                                    p2 -= len(line) + 1

                                y += font.get_height()
                    elif event.key == pygame.K_BACKSPACE:
                        cursor = True
                        if cursorPos > 0:
                            t = files[currFile][1]
                            t = t[:cursorPos - 1] + t[cursorPos:]
                            files[currFile][1] = t
                            cursorPos -= 1
                    elif event.key == pygame.K_DELETE:
                        cursor = True
                        if cursorPos < len(files[currFile][1]):
                            t = files[currFile][1]
                            t = t[:cursorPos] + t[cursorPos + 1:]
                            files[currFile][1] = t
                    elif event.key == pygame.K_F11:
                        t = pygame.time.get_ticks()
                        if t - fullScreenTick >= fullScreenDelay:
                            fullScreenTick = t
                            if not fullscreen:
                                sbf = screen_size
                                w = displaySettings.current_w
                                h = displaySettings.current_h
                                screen = pygame.display.set_mode(
                                    (w, h), pygame.FULLSCREEN)
                                screen_size = [w, h]
                                fullscreen = True
                            else:
                                screen_size = sbf
                                screen = pygame.display.set_mode(sbf, pygame.RESIZABLE)
                                fullscreen = False
                    elif event.unicode in string.printable and event.unicode:
                        if event.unicode == '\r':
                            event.unicode = '\n'
                        cursor = True
                        t = files[currFile][1]
                        t = t[:cursorPos] + event.unicode + t[cursorPos:]
                        files[currFile][1] = t
                        cursorPos += 1
                elif typinginSettings:
                    if event.key == pygame.K_LEFT:
                        if settingsCursor > 0:
                            settingsCursor -= 1
                    elif event.key == pygame.K_RIGHT:
                        if settingsCursor < len(SETTINGS['mbitLocation']):
                            settingsCursor += 1
                    elif event.key == pygame.K_DELETE:
                        if settingsCursor < len(SETTINGS['mbitLocation']):
                            SETTINGS['mbitLocation'] = SETTINGS['mbitLocation'][
                                :settingsCursor] + SETTINGS['mbitLocation'][settingsCursor + 1:]
                    elif event.key == pygame.K_BACKSPACE:
                        if settingsCursor > 0:
                            SETTINGS['mbitLocation'] = SETTINGS['mbitLocation'][
                                :settingsCursor - 1] + SETTINGS['mbitLocation'][settingsCursor:]
                            settingsCursor -= 1
                    elif event.unicode in string.printable and event.unicode:
                        if event.unicode == '\r':
                            event.unicode = '\n'
                        SETTINGS['mbitLocation'] = SETTINGS['mbitLocation'][
                            :settingsCursor] + event.unicode + SETTINGS['mbitLocation'][settingsCursor:]
                        settingsCursor += 1
                elif showTextDialog:
                    if event.key == pygame.K_LEFT:
                        if textDialogCursor > 0:
                            textDialogCursor -= 1
                    elif event.key == pygame.K_RETURN:
                        showTextDialog = False
                        textDialogCommand(textDialogText)
                    elif event.key == pygame.K_RIGHT:
                        if textDialogCursor < len(textDialogText):
                            textDialogCursor += 1
                    elif event.key == pygame.K_DELETE:
                        if textDialogCursor < len(textDialogText):
                            textDialogText = textDialogText[
                                :textDialogCursor] + textDialogText[textDialogCursor + 1:]
                    elif event.key == pygame.K_BACKSPACE:
                        if textDialogCursor > 0:
                            textDialogText = textDialogText[
                                :textDialogCursor - 1] + textDialogText[textDialogCursor:]
                            textDialogCursor -= 1
                    elif event.unicode in string.printable and event.unicode:
                        if event.unicode == '\r':
                            event.unicode = '\n'
                        textDialogText = textDialogText[
                            :textDialogCursor] + event.unicode + textDialogText[textDialogCursor:]
                        textDialogCursor += 1
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 5 and not showFileSelect and not showFileCreate:
                    if pygame.Rect(5, 105, screen_size[0] - 10, textBottom - 105).collidepoint(event.pos):
                        scrollY -= font.get_height() * 4
                        if scrollY < 0 - (lines * font.get_height()) + screen_size[1] - screen_size[1] - 110:
                            scrollY = 0 - (lines * font.get_height()) + \
                                screen_size[1] - screen_size[1] - 110
                    elif console and pygame.Rect(5, textBottom + 5, screen_size[0] - 10, screen_size[1] - 10 - textBottom).collidepoint(event.pos):
                        cscrollY -= font.get_height() * 4
                        clines = len(consoleText.split('\n'))
                        if cscrollY < 0 - (clines * font.get_height()) - screen_size[1] - textBottom:
                            cscrollY = 0 - (clines * font.get_height()
                                            ) - screen_size[1] - textBottom
                elif event.button == 4 and not showFileSelect and not showFileCreate:
                    if pygame.Rect(5, 105, screen_size[0] - 10, textBottom - 105).collidepoint(event.pos):
                        scrollY += font.get_height() * 4
                        if scrollY > 0:
                            scrollY = 0
                    elif console and pygame.Rect(5, textBottom + 5, screen_size[0] - 10, screen_size[1] - 10 - textBottom).collidepoint(event.pos):
                        cscrollY += font.get_height() * 4
                        if cscrollY > 0:
                            cscrollY = 0
                elif event.button == 5 and showFileSelect:
                    if abs(fileSelectScrollY) < (fsy - 13 * 15):
                        fileSelectScrollY -= font.size(' ')[1]
                elif event.button == 4 and showFileSelect:
                    if fileSelectScrollY < 0:
                        fileSelectScrollY += font.size(' ')[1]
                elif event.button == 5:
                    if abs(fileCreateScrollY) < (fcy - 13 * 15):
                        fileCreateScrollY -= font.size(' ')[1]
                elif event.button == 4:
                    if fileCreateScrollY < 0:
                        fileCreateScrollY += font.size(' ')[1]
                elif event.button == 1:
                    if showMessage:
                        showMessage = False
                    else:
                        if pygame.Rect(screen_size[0] - 52, 2, 50, 50).collidepoint(event.pos):
                            menu = not menu
                        else:
                            showAbout = False
                            if menu:
                                y = menuRect.y
                                for mi in menuData:
                                    mr = pygame.Rect(0, 0, 0, 0)
                                    mr.x = menuRect.x
                                    mr.y = y
                                    mr.w = menuWidth
                                    mr.h = font2.size(mi[0])[1]
                                    if mr.collidepoint(event.pos):
                                        if type(mi[1]) != list:
                                            mi[1]()
                                    y += font2.get_height()
                            if menu and showExampleMenu:
                                y = emenuRect.y
                                for mi in exampleMenu:
                                    mr = pygame.Rect(0, 0, 0, 0)
                                    mr.x = emenuRect.x
                                    mr.y = y
                                    mr.w = emenuWidth
                                    mr.h = font2.size(mi[0])[1]
                                    if mr.collidepoint(event.pos):
                                        if type(mi[1]) != list:
                                            mi[1](mi[0])
                                    y += font2.get_height()
                            menu = False
                            if pygame.Rect(screen_size[0] - 105, 2, 50, 50).collidepoint(event.pos):
                                console = not console
                            elif pygame.Rect(screen_size[0] - 158, 2, 50, 50).collidepoint(event.pos):
                                if (not mbedBuilding) and (not mbedUploading):
                                    mbedUploading = True
                                    mbedBuilding = True
                                    consoleText = ""
                                    cscrollY = 0
                                    rstres()
                                    startBuilding()
                            elif pygame.Rect(screen_size[0] - 211, 2, 50, 50).collidepoint(event.pos):
                                if (not mbedBuilding) and (not mbedUploading):
                                    mbedBuilding = True
                                    consoleText = ""
                                    startBuilding()
                            if showSettings and settingsRendered:
                                if quickStartRect.collidepoint(event.pos):
                                    SETTINGS['quickstart'] = not SETTINGS[
                                        'quickstart']
                                if textInputRect.collidepoint(event.pos):
                                    typinginSettings = True
                                else:
                                    typinginSettings = False
                                if darkGreenRect.collidepoint(event.pos):
                                    SETTINGS["theme"] = 'darkgreen'
                                    SETTINGS["highlightColour"] = themes[
                                        'darkgreen'][0]
                                    SETTINGS["darkHighlight"] = themes[
                                        'darkgreen'][1]
                                    SETTINGS["backgroundColour"] = themes[
                                        'darkgreen'][2]
                                elif darkBlueRect.collidepoint(event.pos):
                                    SETTINGS["theme"] = 'darkblue'
                                    SETTINGS["highlightColour"] = themes[
                                        'darkblue'][0]
                                    SETTINGS["darkHighlight"] = themes[
                                        'darkblue'][1]
                                    SETTINGS["backgroundColour"] = themes[
                                        'darkblue'][2]
                                elif darkYellowRect.collidepoint(event.pos):
                                    SETTINGS["theme"] = 'darkyellow'
                                    SETTINGS["highlightColour"] = themes[
                                        'darkyellow'][0]
                                    SETTINGS["darkHighlight"] = themes[
                                        'darkyellow'][1]
                                    SETTINGS["backgroundColour"] = themes[
                                        'darkyellow'][2]
                                elif darkRedRect.collidepoint(event.pos):
                                    SETTINGS["theme"] = 'darkred'
                                    SETTINGS["highlightColour"] = themes[
                                        'darkred'][0]
                                    SETTINGS["darkHighlight"] = themes[
                                        'darkred'][1]
                                    SETTINGS["backgroundColour"] = themes[
                                        'darkred'][2]
                                if not settingsRect.collidepoint(event.pos):
                                    settings()
                            elif showFileSelect and filesRendered:
                                fsy = 0
                                fileSurf.fill((200, 200, 200))
                                dirs = os.listdir(fileSelectDir)
                                dirs.sort()
                                for _file in ['..'] + dirs:
                                    if _file[0] != '.' or _file[:2] == '..':
                                        if os.path.isdir(os.path.join(fileSelectDir, _file)):
                                            _file = _file + os.path.sep
                                        t = font.render(_file, 1, (36, 36, 36))
                                        rect = t.get_rect()
                                        rect.y = fsy + fileSelectScrollY + filesRect.y
                                        rect.x = filesRect.x
                                        rect.w = filesRect.w
                                        if rect.colliderect(filesRect):
                                            if rect.collidepoint(event.pos):
                                                if os.path.isdir(os.path.join(fileSelectDir, _file)):
                                                    if fileSelectSelected == _file:
                                                        fileSelectScrollY = 0
                                                        fileSelectSelected = ''
                                                        fileSelectDir = os.path.join(
                                                            fileSelectDir, _file)
                                                    else:
                                                        fileSelectSelected = _file
                                                else:
                                                    if fileSelectSelected == _file:
                                                        showFileSelect = False
                                                        fileSelectFunc(os.path.join(
                                                            fileSelectDir, _file))
                                                    else:
                                                        fileSelectSelected = _file
                                        fsy += t.get_height()
                                if fsOpenRect.collidepoint(event.pos):
                                    if os.path.isdir(os.path.join(fileSelectDir, fileSelectSelected)):
                                        fileSelectScrollY = 0
                                        fileSelectDir = os.path.join(
                                            fileSelectDir, fileSelectSelected)
                                        fileSelectSelected = ''
                                    else:
                                        showFileSelect = False
                                        fileSelectFunc(os.path.join(
                                            fileSelectDir, _file))
                                elif fsBackRect.collidepoint(event.pos):
                                    showFileSelect = False
                                fileSelectDir = os.path.abspath(fileSelectDir)
                            elif showFileCreate and fileCreateRendered:
                                fcy = 0
                                fileSurf.fill((200, 200, 200))
                                dirs = os.listdir(fileCreateDir)
                                dirs.sort()
                                for _file in ['..'] + dirs:
                                    if _file[0] != '.' or _file[:2] == '..':
                                        if os.path.isdir(os.path.join(fileCreateDir, _file)):
                                            _file = _file + os.path.sep
                                        t = font.render(_file, 1, (36, 36, 36))
                                        rect = t.get_rect()
                                        rect.y = fcy + fileCreateScrollY + filescerRect.y
                                        rect.x = filescerRect.x
                                        rect.w = filescerRect.w
                                        if rect.colliderect(filescerRect):
                                            if rect.collidepoint(event.pos):
                                                if os.path.isdir(os.path.join(fileCreateDir, _file)):
                                                    if fileCreateSelected == _file:
                                                        fileCreateScrollY = 0
                                                        fileCreateSelected = ''
                                                        fileCreateDir = os.path.join(
                                                            fileCreateDir, _file)
                                                    else:
                                                        fileCreateSelected = _file
                                                else:
                                                    if fileCreateSelected != _file:
                                                        #		showFileCreate = False
                                                        #		#fileCreateFunc(os.path.join(fileCreateDir, _file))
                                                        #	else:
                                                        fileCreateSelected = _file
                                        fcy += t.get_height()
                                if fcOpenRect.collidepoint(event.pos):
                                    if os.path.isdir(os.path.join(fileSelectDir, fileSelectSelected)):
                                        fileCreateScrollY = 0
                                        fileCreateDir = os.path.join(
                                            fileSelectDir, fileSelectSelected)
                                        fileCreateSelected = ''
                                elif fcBackRect.collidepoint(event.pos):
                                    showFileCreate = False
                                elif fcSelectRect.collidepoint(event.pos):
                                    showFileCreate = False
                                    askstring("File Name:", saveFile)
                                fileCreateDir = os.path.abspath(fileCreateDir)
                            elif showQuery and queryRendered:
                                if queryNoRect.collidepoint(event.pos):
                                    showQuery = False
                                elif queryYesRect.collidepoint(event.pos):
                                    showQuery = False
                                    exec(queryCommand, globals(), locals())
                            elif showTextDialog and textDialogRendered:
                                if textDialogCancelRect.collidepoint(event.pos):
                                    showTextDialog = False
                                elif textDialogOkayRect.collidepoint(event.pos):
                                    showTextDialog = False
                                    textDialogCommand(textDialogText)
                            else:
                                for n, f in enumerate(fileRects):
                                    if f.collidepoint(event.pos):
                                        if n == len(fileRects) - 1:
                                            askstring("New File Name:", newFile)
                                        else:
                                            r = pygame.Rect(f)
                                            nw = font2.size(' x ')[0]
                                            r.x = r.x + r.w - nw
                                            r.w = nw
                                            if r.collidepoint(event.pos):
                                                askyesno(
                                                    "Are you sure you want to delete this file?", 'delopenfile(%d)' % n)
                                            else:
                                                currFile = n
                                                cursorPos = 0
                                                scrollY = 0

                                hit = False
                                y = 105 + scrollY
                                p = 0
                                for n, line in enumerate(files[currFile][1].split('\n')):
                                    if y < textBottom and y > 100 and not hit:
                                        x = sp + 5
                                        for cn, c in enumerate(line + ' '):
                                            if c == '	':
                                                c = '    '
                                            if c not in renderedChars:
                                                t = font.render(
                                                    c, 1, SETTINGS['backgroundColour'])
                                                renderedChars[c] = t
                                            else:
                                                t = renderedChars[c]
                                            rect = t.get_rect()
                                            rect.x = x
                                            rect.y = y
                                            if rect.collidepoint(event.pos):
                                                hit = True
                                                cursorPos = p
                                                cursor = True
                                            x += t.get_width()
                                            p += 1
                                    else:
                                        for cn, c in enumerate(line + ' '):
                                            p += 1
                                    y += font.get_height()
                                if not hit:
                                    y = 105 + scrollY
                                    p = 0
                                    for n, line in enumerate(files[currFile][1].split('\n')):
                                        p += len(line) + 1
                                        if y < textBottom and y > 100:
                                            x = sp + 5
                                            t = font.render(line, 1, SETTINGS[
                                                            'backgroundColour'])
                                            rect = t.get_rect()
                                            rect.x = x
                                            rect.y = y
                                            rect.w = screen_size[0] - 10
                                            if rect.collidepoint(event.pos):
                                                hit = True
                                                cursorPos = p - 1
                                                cursor = True
                                        y += font.get_height()
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                screen_size = event.size
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == 29:
                cursor = not cursor
except Exception as e:
    import traceback
    tb = traceback.format_exc()
    print('')
    print("#" * len(max(tb.split('\n'), key=len)))
    print("ERROR")
    print("#" * len(max(tb.split('\n'), key=len)))
    print(tb)
    print("#" * len(max(tb.split('\n'), key=len)))

    lines = tb.split('\n')
    lines += ["Hit Any Key To Exit"]

    import pygame
    pygame.init()
    f = pygame.font.SysFont("monospace", 24)
    func = lambda x:f.size(x)[0]
    width = f.size(max(lines, key=func))[0]
    height = len(lines) * f.size('text')[1]
    d = pygame.display.set_mode((width, height), pygame.NOFRAME)
    pygame.display.set_caption("Micro:Bit - Error!", "Micro:Bit - Error!")
    d.fill((36, 36, 36))
    y = (d.get_height() - len(lines) * f.size('text')[1]) / 2
    for l in lines:
        t = f.render(l, 1, (73, 182, 73))
        x = 0
        d.blit(t, (x, y))
        y += t.get_height()
    running = True
    while running:
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                running = False
