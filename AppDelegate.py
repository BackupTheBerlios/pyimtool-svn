#
#  AppDelegate.py
#  PyImtool
#
#  Created by Francesco Pierfederici on Thu Jun 03 2004.
#  Copyright (c) 2004 Francesco Pierfederici. All rights reserved.
#

# globals and the like
from utilities import *

# my own classes
from PrefsController import *
from InfoController import *
from DataListener import *
from FrameBuffer import *
from PyImageView import *
from PyImage import *




NibClassBuilder.extractClasses ("MainMenu")

class AppDelegate (NibClassBuilder.AutoBaseClass):
    """
    This, in a sense, is the main application. It is here that we 
    setup all the various bits and pieces that make up our app.
    
    This class is defined in MainMenu.nib and, therefore is already
    instantiated (it is like it has been pickled). This is why we do
    not have a Python constructor method: it would never get called.
    
    This class has some instance variables already defined in the NIB
    file. These are:
    imageView
    
    """
    def init (self):
        """
        Initialization method. Sets instance variables ro defult 
        values. It also takes care of initializing the 
        preferences dictionary (PREFS).
        
        This is the Cocoa init method, not the Python __init__.
        """
        self.inetDataThread = None
        self.unixDataThread = None
        self.infoPanel = None
        
        # read the application preferences
        prefs = NSUserDefaults.standardUserDefaults ()
        
        # do we have a preferences file, already?
        if (prefs.boolForKey_ ('HasPrefsFile')):
            for key in PREFS.keys ():
                value = prefs.boolForKey_ (key)
                PREFS[key] = value
        
        # Create a dict of FrameBuffer instances. These will hold
        # the image data that we are going to display. At first, we
        # just need to create one FrameBuffer object.
        # The format of the dict is quite simple: 
        # {index: FrameBuffer}
        # 
        # We use a dictionary so that we can remove frames without
        # worrying about keeping them in order.
        self.frameBuffers = {0: FrameBuffer ()}
        self.currentFrame = 0
        
        super (AppDelegate, self).init ()   
        return (self)
    
    
    def applicationDidFinishLaunching_ (self, aNotification):
        """
        The application is ready. We start the DataListener threads
        if needed.
        """
        # Remove any leftover UNIX pipe.
        try:
            os.remove (UNIX_ADDR)
        except:
            pass
        
        # Start the data listener threads, if appropriate.
        if (PREFS['EnableIRAFIntegration']):
            self.inetDataThread = DataListener (sockType='inet', controller=self)
            self.inetDataThread.start ()
            
            self.unixDataThread = DataListener (sockType='unix', controller=self)
            self.unixDataThread.start ()
        return
    
    
    def displayImage (self):
        """
        This method gets called by the active RequestHandler object
        as soon as it is done reading image data. This means that we
        can be confident that the current frame buffer (identified by
        self.curentFrame) is properly setup.
        """
        self.imageView.display (self.frameBuffers[self.currentFrame])
        return
    
    
    def initFrame (self, fbIndex):
        """
        Erases the fbIndex-th FrameBuffer object in self.frameBuffers
        and returns the (empty) FrameBuffer.
        """
        n = len (self.frameBuffers)
        if (fbIndex >= n):
            # we need to create a new FrameBuffer object (and 
            # possibly intermediate FrameBuffers as well).
            for i in range (n, bdIndex + 1):
                self.frameBuffers[i] = FrameBuffer ()
        else:
            # The FrameBuffer object we are interested in already 
            # exists: erase it. Foe efficiency sake, we just delete
            # it and create a new (empty) one.
            del (self.frameBuffers[fbIndex])
            self.frameBuffers[fbIndex] = FrameBuffer ()
        # return the fbIndex-th frame.
        return (self.frameBuffers[fbIndex])
    
    
    def setCurrentFrame (self, fbIndex):
        if (fbIndex >= len (self.frameBuffers)):
            raise (IndexError, 'framebuffer index out of range')
        else:
            self.currentFrame = fbIndex
        return
    
    
    def getFrame (self, fbIndex):
        if (fbIndex >= len (self.frameBuffers)):
            raise (IndexError, 'framebuffer index out of range')
        else:
            return (self.frameBuffers[fbIndex])
        return (None)
    
    
    def showInfoWindow_ (self, sender):
        """
        Simply opens a new panel with general information about the
        image being displayed (self.currentFrame).
        
        If the sender's title is "Hide Info Window" it closes the 
        panel.
        """
        if (sender.title ()[0] == 'H'):
            # close the info panel
            self.infoPanel.closeWindow (self)
            # set the menu item title to "Show..."
            sender.setTitle_ ('Show Info Panel')
        else:
            self.infoPanel = InfoController.infoController (self.imageView)
            self.infoPanel.showWindow_ (self)
            # set the menu item title to "Hide..."
            sender.setTitle_ ('Hide Info Panel')
        return
    
    
    def showHeaderWindow_ (self, sender):
        """
        Opens a separate window wwith the header information from the
        currently displayed image (if possible).
        """
        print ('headerWindow')
        return
    
    
    def showPrefsWindow_ (self, sender):
        """
        Shows the Preferences window
        """
        PrefsController.prefsController ().showWindow_ (self)
        return
    
        
