#
#  CoordTransf.py
#  PyImtool
#
#  Created by Francesco Pierfederici on Thu Jun 03 2004.
#  Copyright (c) 2004 Francesco Pierfederici. All rights reserved.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

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
        self.imTitle = ''       # image title from WCS
        # physical -> celestial
        self.regId = None
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