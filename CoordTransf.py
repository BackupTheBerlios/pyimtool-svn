#
#  CoordTransf.py
#  pyimtool3
#
#  Created by Francesco Pierfederici on Thu Jun 03 2004.
#  Copyright (c) 2004 __MyCompanyName__. All rights reserved.
#
from utilities import *

class CoordTransf (object):
    def __init__ (self):
        # coordinate transformation:
        # screen -> physical
        self.valid = 0          # has the WCS been validated/parsed?
        self.a = 1              # x scale factor
        self.b = 0              # y scale factor
        self.c = 0              # x cross factor
        self.d = 1              # y cross factor
        self.tx = 0             # translation in x
        self.ty = 0             # translation in y
        self.z1 = 0             # min greyscale value
        self.z2 = 1             # max greyscale value
        self.zt = W_UNITARY     # gretscale mapping
        self.format = ''        # WCS output format
        self.imtitle = ''       # image title from WCS
        # physical -> celestial
        self.regid = None
        self.id = None
        self.ref = ''
        self.region = ''
        self.sx = 1.0
        self.sy = 1.0
        self.snx = DEF_FRAME_WIDTH
        self.sny = DEF_FRAME_WIDTH
        self.dx = 1
        self.dy = 1
        self.dnx = DEF_FRAME_WIDTH
        self.dny = DEF_FRAME_WIDTH
        return