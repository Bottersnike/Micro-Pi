import re
import os

def parse(error):
    re1 ='((?:\\/[\\w\\.\\-]+)+)'    # Unix Path 1
    re2 ='(:)'   # Any Single Character 1
    re3 ='(\\d+)'    # Integer Number 1
    re4 ='(:)'   # Any Single Character 2
    re5 ='(\\d+)'    # Integer Number 2
    re6 ='(:)'   # Any Single Character 3
    re7 ='.*?'   # Non-greedy match on filler
    re8 ='(error: )'   # Word 1
    re9 ='(.+?(?=\\n))'

    rg = re.compile(re1+re2+re3+re4+re5+re6+re7+re8+re9,re.IGNORECASE|re.DOTALL)
    print rg.pattern
    ms = rg.findall(error)
    rtns = []
    for m in ms:
        if m:
            d = (os.path.basename(m[0]), int(m[2]), int(m[4]), m[7])
            rtns.append(d)
    return rtns

if __name__ == "__main__":
    print parse("/home/pi/.micropi/buildEnv/source/main.cpp:6:2: error: 'text' was not declared in this scope")
