#
#  FrameBuffer.py
#  PyImtool
#
#  Created by Francesco Pierfederici on Thu Jun 03 2004.
#  Copyright (c) 2004 Francesco Pierfederici. All rights reserved.
#
from utilities import *
from CoordTransf import *

class FrameBuffer (object):
    def __init__ (self):
        self.width = None           # wirdth of the framebuffer
        self.height = None          # height of the framebuffer
        self.imgWidth = None       # wirdth of the image
        self.imgHeight = None      # height of the image
        self.config = None          # framebuffer config index
                                    # (see fbconfigs dictionary)
        self.wcs = None             # WCS
        self.image = None           # the image data itself
        self.bitmap = None          # the image bitmap
        self.buffer = None          # used for screen updates
        self.zoom = 1.0             # zoom level
        self.ct = CoordTransf ()
        
        self.bitsPerSample = 8
        self.samplesPerPixel = 1
        self.hasAlpha = False
        self.isPlanar = True
        self.colorSpaceName = NSCalibratedWhiteColorSpace
        return
    
    

