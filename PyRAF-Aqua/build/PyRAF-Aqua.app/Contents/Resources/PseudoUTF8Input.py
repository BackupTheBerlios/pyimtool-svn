
from utilities import *

class PseudoUTF8Input(object):
    softspace = 0
    def __init__(self, readlinemethod):
        self._buffer = u''
        self._readline = readlinemethod

    def read(self, chars=None):
        if chars is None:
            if self._buffer:
                rval = self._buffer
                self._buffer = u''
                if rval.endswith(u'\r'):
                    rval = rval[:-1]+u'\n'
                return rval.encode('utf-8')
            else:
                return self._readline(u'\x04')[:-1].encode('utf-8')
        else:
            while len(self._buffer) < chars:
                self._buffer += self._readline(u'\x04\r')
                if self._buffer.endswith('\x04'):
                    self._buffer = self._buffer[:-1]
                    break
            rval, self._buffer = self._buffer[:chars], self._buffer[chars:]
            return rval.encode('utf-8').replace('\r','\n')

    def readline(self):
        if u'\r' not in self._buffer:
            self._buffer += self._readline(u'\x04\r')
        if self._buffer.endswith('\x04'):
            rval = self._buffer[:-1].encode('utf-8')
        elif self._buffer.endswith('\r'):
            rval = self._buffer[:-1].encode('utf-8')+'\n'
        self._buffer = u''

        return rval
