#
#  PrefController.py
#  PyImtool
#
#  Created by Francesco Pierfederici on Thu Jun 03 2004.
#  Copyright (c) 2004 Francesco Pierfederici. All rights reserved.
#
# globals and the like
from utilities import *


from PyObjCTools import NibClassBuilder
NibClassBuilder.extractClasses("Preferences")



# class defined in Preferences.nib
class PrefsController (NibClassBuilder.AutoBaseClass):
    # the actual base class is WSTConnectionWindowController
    # The following outlets are added to the class:
    # inetSockets
    # unixSockets
    # imageScale
    
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
    
    def prefsController (self):
        return (PrefsController.alloc ().init ())
    
    prefsController = classmethod (prefsController)
    
    def init (self):
        self = self.initWithWindowNibName_ ("Preferences")
        
        super (PrefsController, self).init ()
        return (self)
    
    
    def awakeFromNib (self):
        self.retain()
        
        # check the preferences and set the check-boxes
        # accordingly.
        if (PREFS['EnableUNIXSockets']):
            self.unixSockets.setState_ (NSOnState)
        else:
            self.unixSockets.setState_ (NSOffState)
        
        if (PREFS['EnableINETSockets']):
            self.inetSockets.setState_ (NSOnState)
        else:
            self.inetSockets.setState_ (NSOffState)
        
        self.imageScale.deselectAllCells ()
        if (PREFS['ScaleToFit']):
            self.imageScale.selectCellAtRow_column_ (1, 0)
        else:
            self.imageScale.selectCellAtRow_column_ (0, 0)
        
        return
    
    
    def checkBoxSelected_ (self, sender):
        # update our internal preference dictionary
        # with the new values
        try:
            state = sender.state ()
        except:
            pass
        nthreads = 0
        value = None
        
        if (sender == self.unixSockets):
            key = 'EnableUNIXSockets'
        elif (sender == self.inetSockets):
            key = 'EnableINETSockets'
        elif (sender == self.imageScale):
            # self.imageScale is a NSMatrix. The first
            # is for "actual_size" behaviour, the second
            # is for "zoom_to_fit"
            value = sender.selectedRow ()
            key = 'ScaleToFit'
        else:
            return
        
        # determine the value
        if (value == None):
            if (state == NSOnState or state == NSMixedState):
                value = 1
            else:
                value = 0
        
        # update our internal preferences dictionary
        PREFS[key] = value
        
        return
    
    
    def windowShouldClose_ (self, sender):
        nthreads = 0
        
        # here we want to make sure that at least one 
        # Data Thread is selected...
        if (PREFS['EnableUNIXSockets']):
            nthreads += 1
        if (PREFS['EnableINETSockets']):
            nthreads += 1
        
        if (nthreads == 0):
            # display an alert!
            answer = NSRunAlertPanel ('Data Input Threads', 
                                      'At least one of the checkboxes for IRAF Integration must be selected!',
                                      'Ok',
                                      nil,
                                      nil)
            # select the proper tab
            self.tabView.selectTabViewItemAtIndex_ (1)
            return (NO)
        else:
            # save the preferences on file
            prefs = NSUserDefaults.standardUserDefaults ()
            for key in PREFS.keys ():
                # update the application preferences
                prefs.setBool_forKey_ (PREFS[key], key)
            # and acknowledge the fact that, now, we have a 
            # preferences file!
            prefs.setBool_forKey_ (True, 'HasPrefsFile')
            return (YES)
    
    
    def windowWillClose_ (self, notification):
        self.autorelease()
        
        return











