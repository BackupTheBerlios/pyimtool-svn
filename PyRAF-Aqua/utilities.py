import os
import sys
import traceback
import sets
import keyword
import time
from code import InteractiveConsole, softspace
from StringIO import StringIO

from objc import YES, NO, selector
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder

# PyRAF needs the env. variables TERM, iraf, IRAFARCH
if (not os.environ.has_key ('TERM')):
    os.environ['TERM'] = 'vt100'
if (not os.environ.has_key ('iraf')):
    os.environ['iraf'] = '/iraf/iraf'
if (not os.environ.has_key ('IRAFARCH')):
    os.environ['IRAFARCH'] = 'macosx'

# We need to access login.cl


