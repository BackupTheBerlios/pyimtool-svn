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
    
    def infoController (self, app, view):
        return (InfoController.alloc ().init (app, view))
    
    infoController = classmethod (infoController)
    
    def init (self, app, view):
        self = self.initWithWindowNibName_ ("InfoPanel")
        self.imageView = view
        self.appDelegate = app
        
        super (InfoController, self).init ()
        return (self)
    
    
    def awakeFromNib (self):
        self.retain()
        
        # start the MagnifiedView
        self.magnifiedView.startWithMagnification_crosshairSize_updateInterval_ (4, 10, 0.05)
        self.magnifiedView.stop ()
        
        # tell the main window to start tracking the mouse.
        self.imageView.startTrackingMouse (self)
        return
    
    
    def windowShouldClose_ (self, sender):
        # tell the main window to stop tracking the mouse.
        self.imageView.stopTrackingMouse ()
        return (True)
    
    
    def windowWillClose_ (self, notification):
        # tell the main window to stop tracking the mouse.
        self.appDelegate.infoWindowWillClose ()
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
    
     
    def enableMagnifier (self):
        self.magnifiedView.start ()
        return
    
    
    def disableMagnifier (self):
        self.magnifiedView.stop ()
        return











