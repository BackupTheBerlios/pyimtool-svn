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



