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
    
    def infoController (self):
        return (InfoController.alloc ().init ())
    
    infoController = classmethod (infoController)
    
    def init (self):
        self = self.initWithWindowNibName_ ("InfoPanel")
        
        super (InfoController, self).init ()
        return (self)
    
    
    def awakeFromNib (self):
        self.retain()
        # tell the main window to start tracking the mouse.
        return
    
    
    def windowShouldClose_ (self, sender):
        # tell the main window to stop tracking the mouse.
        return (True)
    
    
    def windowWillClose_ (self, notification):
        self.autorelease()
        return











