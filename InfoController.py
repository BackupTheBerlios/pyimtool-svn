#
#  InfoController.py
#  PyImtool
#
#  Created by Francesco Pierfederici on Thu Jun 03 2004.
#  Copyright (c) 2004 Francesco Pierfederici. All rights reserved.
#
# globals and the like
from utilities import *


from PyObjCTools import NibClassBuilder
NibClassBuilder.extractClasses("InfoPanel")


# load the MagnifiedView class
path = os.path.abspath (os.path.join (PATH, '../Resources/MagnifiedView.bundle'))
print (path)
import objc
objc.loadBundle ('MagnifiedView', globals (), bundle_path=path)
MagnifiedView = objc.lookUpClass ('MagnifiedView')
del objc


# class defined in InfoPanel.nib
class InfoController (NibClassBuilder.AutoBaseClass):
    # the actual base class is WSWindowController
    # The following outlets are added to the class:
    # window
    # [x|y|int|name|title|ext]Filed
    
    __slots__ = ('_toolbarItems',
        '_toolbarDefaultItemIdentifiers',
        '_toolbarAllowedItemIdentifiers',
        '_methods',
        '_methodSignatures',
        '_methodDescriptions',
        '_server',
        '_methodPrefix',
        '_workQueue',
        '_working',
        '_workerThread',
        '_windowIsClosing')
    
    def infoController (self, view):
        return (InfoController.alloc ().init (view))
    
    infoController = classmethod (infoController)
    
    def init (self, view):
        self = self.initWithWindowNibName_ ("InfoPanel")
        self.imageView = view
        
        super (InfoController, self).init ()
        return (self)
    
    
    def awakeFromNib (self):
        self.retain()
        
        # start the MagnifiedView
        self.magnifiedView.startWithMagnification_crosshairSize_updateInterval_ (4, 10, 0.05)
        
        # tell the main window to start tracking the mouse.
        self.imageView.startTrackingMouse (self)
        return
    
    
    def windowShouldClose_ (self, sender):
        # tell the main window to stop tracking the mouse.
        self.imageView.stopTrackingMouse ()
        return (True)
    
    
    def windowWillClose_ (self, notification):
        # tell the main window to stop tracking the mouse.
        self.imageView.stopTrackingMouse ()
        self.autorelease ()
        return
    
    
    def closeWindow (self, sender):
        self.window ().performClose_ (sender)
        return
    
    
    def setField (self, fieldName, value):
        if (fieldName == 'title'):
            self.titleField.setStringValue_ (str (value))
        elif (fieldName == 'name'):
            self.nameField.setStringValue_ (str (value))
        elif (fieldName == 'ext'):
            self.extField.setStringValue_ (str (value))
        elif (fieldName == 'x'):
            self.xField.setStringValue_ (str (value))
        elif (fieldName == 'y'):
            self.yField.setStringValue_ (str (value))
        elif (fieldName == 'int'):
            self.intField.setStringValue_ (value)
        else:
            pass
        return
    
     










