"""
DstImageView.py
"""

from PyObjCTools import NibClassBuilder, AppHelper
from objc import getClassList, objc_object
from AppKit import *
from Foundation import *




class DstImageView(NibClassBuilder.AutoBaseClass):
    def isFlipped(self):
        return(True)







