"""
SrcImageView.py
"""

from PyObjCTools import NibClassBuilder, AppHelper
from objc import getClassList, objc_object
from AppKit import *
from Foundation import *




class SrcImageView(NibClassBuilder.AutoBaseClass):
    def awakeFromNib(self):
        self.notificationCenter = NSNotificationCenter.defaultCenter()
        return
    
    def setImage_(self, image):
        super(SrcImageView, self).setImage_(image)
        # Send a notification that the image has changed
        self.notificationCenter.postNotificationName_object_('srcImageUpdated', 
            image)
        return





