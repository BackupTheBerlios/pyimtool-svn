#
#  utilities.py
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

from AppKit import *
from Foundation import *

from objc import *

from PyObjCTools import NibClassBuilder, AppHelper
import threading, time, struct, glob
import socket, SocketServer, sys
import os, string
import numarray
import copy


# global variables and classes
try:
    PORT = int (os.environ['IMTDEV'])
except:
    PORT = 5137
HOST = ''
UID = os.getuid ()
UNIX_ADDR = '/tmp/.IMT' + str (UID)
NCONNECTIONS = 5

DEFAULT_LUT = 'standard'

# internal globals
MEMORY            = 01              # frame buffer i/o
LUT               = 02              # lut i/o
FEEDBACK          = 05              # used for frame clears
IMCURSOR          = 020             # logical image cursor
WCS               = 021             # used to set WCS

IIS_VERSION	      = 10              # version 1.0

PACKED            = 0040000
COMMAND           = 0100000
IIS_READ          = 0100000
IMC_SAMPLE        = 0040000
IMT_FBCONFIG      = 077
XYMASK            = 077777

MAX_FBCONFIG      = 128             # max possible frame buf sizes
MAX_FRAMES        = 15              #  max number of frames (start from 0)
MAX_CLIENTS       = 8               #  max display server clients
DEF_NFRAMES       = 1               #  save memory; only one frame
DEF_FRAME_WIDTH   = 512             #  512 square frame
DEF_FRAME_HEIGHT  = 512             #  512 square frame

SZ_LABEL          = 256             #  main frame label string
SZ_IMTITLE        = 128             # image title string
SZ_WCSBUF         = 1024            # WCS text buffer size
SZ_OLD_WCSBUF     = 320             # old WCS text buffer size
SZ_FIFOBUF        = 4000            # transfer size for FIFO i/o
SZ_FNAME          = 256
SZ_LINE           = 256
SZ_IMCURVAL       = 160

# WCS definitions.
W_UNITARY         = 0
W_LINEAR          = 1
W_LOG             = 2
W_DEFFORMAT       = " %7.2f %7.2f %7.1f%c"

VERBOSE           = 1

# GUI constants
MAX_PROGR         = 100
MIN_PROGR         = 0
MAX_CONTRAST      = 5.


PATH = os.path.dirname (sys.argv[0])
RESOURCES_PATH = os.path.abspath (os.path.join (PATH, '../Resources'))

# cursor position
cursor_x = 1.0
cursor_y = 1.0

# we need a way to tell which frame buffer corresponds 
# to which tab (in the NSTabView). Both are 0 indexed.
tabFrame_mapping = {}

# Frame buffer configurations
fbconfigs = {1: [2, 512, 512], 
    2: [2, 800, 800], 
    3: [2, 1024, 1024], 
    4: [1, 1600, 1600], 
    5: [1, 2048, 2048], 
    6: [1, 4096, 4096], 
    7: [1, 8192, 8192], 
    8: [1, 1024, 4096], 
    9: [2, 1144, 880], 
    10: [2, 1144, 764], 
    11: [2, 128, 128], 
    12: [2, 256, 256], 
    13: [2, 128, 1056], 
    14: [2, 256, 1056], 
    15: [2, 1056, 128], 
    16: [2, 1056, 256], 
    17: [2, 1008, 648], 
    18: [2, 1024, 680], 
    19: [1, 4096, 1024], 
    20: [2, 388, 576], 
    21: [1, 3040, 976], 
    22: [1, 128, 1520], 
    23: [1, 256, 1520], 
    24: [1, 512, 1520], 
    25: [1, 960, 1520], 
    26: [1, 1232, 800], 
    27: [1, 3104, 512], 
    28: [1, 976, 3040], 
    29: [1, 800, 256], 
    30: [1, 256, 800], 
    31: [1, 1240, 400], 
    32: [2, 832, 800], 
    33: [2, 544, 512], 
    34: [1, 1056, 1024], 
    35: [1, 2080, 2048], 
    36: [2, 832, 820], 
    37: [2, 520, 512], 
    38: [1, 3104, 1024], 
    39: [1, 1232, 800], 
    40: [4, 1200, 600], 
    41: [1, 8800, 8800], 
    42: [1, 4400, 4400], 
    43: [1, 2200, 2200], 
    44: [1, 1100, 1100], 
    45: [1, 2080, 4644], 
    46: [1, 6400, 4644], 
    47: [1, 3200, 2322], 
    48: [1, 1600, 1161], 
    49: [1, 800, 581], 
    50: [1, 2048, 2500]}

# Application-wide preferences
PREFS = {'ScaleToFit': True, 
         'EnableIRAFIntegration': True,
         'CheckForNewVersion': False}

# PyImtool Home Page
HOME_PAGE = 'http://pyimtool.berlios.de'

# Toolbar icon labels
TOOLBAR_LABELS = ('zoomIn', 
                  'zoomOut', 
                  'zoomToFit', 
                  'actualSize', 
                  'prev', 
                  'next')


# utility routines
def wcsPixTransform (ct, i, format=0):
    """Computes the WCS corrected pixel value given a coordinate 
    transformation and the raw pixel value.
    
    Input:
    ct      coordinate transformation. instance of coord_tran.
    i       raw pixel intensity.
    format  format string (optional).
    
    Returns:
    WCS corrected pixel value
    """
    z1 = float (ct.z1)
    z2 = float (ct.z2)
    i = float (i)
    
    yscale = 128.0 / (z2 - z1)
    if (format == 'T' or format == 't'):
        format = 1
    
    if (i == 0):
        t = 0.
    else:
        if (ct.zt == W_LINEAR):
            t = ((i - 1) * (z2 - z1) / 199.0) + z1;
            t = max (z1, min (z2, t))
        else:
            t = float (i)
    if (format > 1):
        t = (z2 - t) * yscale
    return (t)


def wcsCoordTransform (ct, x, y):
    """Computes tha WCS corrected pixel coordinates (RA and Dec
    in degrees) given a coordinate transformation and the screen 
    coordinates (x and y, in pixels).
    
    Input:
    ct      coordinate transformation. instance of coord_tran.
    x       x coordinate in pizels.
    y       y coordinate in pixels.
    
    Returns:
    (RA, Dec) in degrees (as floats).
    """
    x = float (x)
    y = float (y)
    if (ct.valid):
        # The imtool WCS assumes that the center of the first display
        # pixel is at (0,0) but actually it is at (0.5,0.5).
        x -= 0.5
        y -= 0.5
        
        if (abs(ct.a) > .001):
            ra = ct.a * x + ct.c * y + ct.tx
        if (abs(ct.d) > .001):
            dec = ct.b * x + ct.d * y + ct.ty
    else:
        ra = x
        dec = y
    return ((ra, dec))


def sex2deg(sex, sep=':'):
    try:
        (dd, mm, ss) = string.split(string.strip(sex), sep)
    except:
        (dd, mm) = string.split(string.strip(sex), sep)
        ss = '0'
    if(float(dd) >= 0):
        return(float(dd) + float(mm) / 60.0 + float(ss) / 3600.0)
    else:
        return(float(dd) - float(mm) / 60.0 - float(ss) / 3600.0)


def deg2sex (deg, sep=':'):
    try:
        deg = float (deg)
    except:
        return ('')
    
    degrees = int (deg)
    if(degrees >= 0):
        temp = (deg - degrees) * 60
        minutes = int (temp)
        seconds = int ((temp - minutes) * 60)
    else:
        temp = - (deg - degrees) * 60
        minutes = int (temp)
        seconds = int ((temp - minutes) * 60)
    
    sex = "%02d%c%02d%c%05.2f" % (degrees, sep, minutes, sep, seconds)
    return (sex)


def rightPad (strg, length, ch=' '):
    """As seen on http://www.halfcooked.com/mt/archives/000640.html"""
    return (strg + ch * (length - len(strg)))


