#
#  FrameBuffer.py
#  pyimtool3
#
#  Created by Francesco Pierfederici on Thu Jun 03 2004.
#  Copyright (c) 2004 __MyCompanyName__. All rights reserved.
#
from utilities import *
from coord_tran import *

class FrameBiffer (object):
    def __init__ (self):
        self.width = None           # wirdth of the framebuffer
        self.height = None          # height of the framebuffer
        self.img_width = None       # wirdth of the image
        self.img_height = None      # height of the image
        self.config = None          # framebuffer config index
                                    # (see fbconfigs dictionary)
        self.wcs = None             # WCS
        self.image = None           # the image data itself
        self.bitmap = None          # the image bitmap
        self.buffer = None          # used for screen updates
        self.zoom = 1.0             # zoom level
        self.ct = CoordTransf ()
        return
