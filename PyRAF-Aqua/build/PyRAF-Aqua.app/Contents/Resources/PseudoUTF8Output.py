
from utilities import *

class PseudoUTF8Output(object):
    softspace = 0
    def __init__(self, writemethod):
        self._write = writemethod

    def write(self, s):
        if not isinstance(s, unicode):
            s = s.decode('utf-8', 'replace')
        self._write(s)

    def writelines(self, lines):
        for line in lines:
            self.write(line)

    def flush(self):
        pass

    def isatty(self):
        return True
