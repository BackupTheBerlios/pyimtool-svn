#
#  FrameBuffer.py
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
    
    

