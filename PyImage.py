#
#  PyImage.py
#  pyimtool3
#
#  Created by Francesco Pierfederici on Thu Jun 03 2004.
#  Copyright (c) 2004 __MyCompanyName__. All rights reserved.
#

import string
from utilities import *

class PyImage (object):
    def __init__ (self, header=None, data=None):
        self.initHeader (header)
        self.data = data
    
    def initHeader (self, header):
        self.title = None
        self.width = None
        self.height = None
        self.bitsPerSample = None
        self.samplesPerPixel = None
        self.isPlanar = True
        self.hasAlpha = False
        self.colorSpaceName = None
        self.bytesPerRow = None
        self.fileName = None
        
        if (header):
            for key in header.keys ():
                method_name = 'set' + string.upper (key[0]) + key[1:]
                method = getattr (self, method_name)
                method (header[key])
                continue
                try:
                    method = getattr (self, method_name)
                except:
                    if (VERBOSE):
                        print ('WARNING: ' + method_name + 
                            ' is not a supported method.')
                    continue
                try:
                    method (header[key])
                except:
                    if (VERBOSE):
                        print ('WARNING: ' + method + ' (' + 
                            str (header[key]) + ') failed.')
                    continue
    
    def setTitle (self, t):
        self.title = str (t)
    
    def setData (self, d):
        self.data = d
    
    def setWidth (self, w):
        self.width = int (w)
    
    def setHeight (self, h):
        self.height = int (h)
    
    def setSize (self, (w, h)):
        (self.width, self.height) = (int (w), int (h))
    
    def setBitsPerSample (self, bps):
        self.bitsPerSample = int (bps)
    
    def setSamplesPerPixel (self, spp):
        self.samplesPerPixel = int (spp)
    
    def setIsPlanar (self, p):
        self.isPlanar = bool (int (p))
    
    def setHasAlpha (self, a):
        self.hasAlpha = bool (int (a))
    
    def setColorSpaceName (self, c):
        self.colorSpaceName = str (c)
    
    def setBytesPerRow (self, bpr):
        self.bytesPerRow = int (bpr)
    
    def setFileName (self, f):
        self.fileName = str (f)
    