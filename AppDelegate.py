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
from DataListener import *
from FrameBuffer import *
from PyImageView import *
from PyImage import *




NibClassBuilder.extractClasses ("MainMenu")

class AppDelegate (NibClassBuilder.AutoBaseClass):
    def init (self):
        """
        Initialization method. Sets instance variables ro defult 
        values. It also takes care of initializing the 
        preferences dictionary (PREFS).
        
        This is the Cocoa init method, not the Python __init__.
        """
        self.inetDataThread = None
        self.unixDataThread = None
        
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
    
    
    def awakeFromNib (self):
        """
        Here we simply setup the User Interface.
        """
        # setup the GUIs
        return
        
    
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
    
    
    def updateImage (self):
        # if this gets called, that means that 
        # we should rebuild self.image using 
        # self.header and self.data
        self.image = PyImage (self.header, self.data)
        
        self.imgView.display (self.image)
        return
    
    
    def displayImage (self):
        """
        This method gets called by the active RequestHandler object
        as soon as it is done reading image data. This means that we
        can be confident that the current frame buffer (identified by
        self.curentFrame) is properly setup.
        """
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
        if (fnIndex >= len (self.frameBuffers)):
            raise (IndexError, 'framebuffer index out of range')
        else:
            self.currentFrame = fbIndex
        return
    
    
    def getFrame (self, fbIndex):
        if (fnIndex >= len (self.frameBuffers)):
            raise (IndexError, 'framebuffer index out of range')
        else:
            return (self.frameBuffers[fbIndex])
        return (None)
    


