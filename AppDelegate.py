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
from WindowDelegate import *
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
    file.
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
        self.toolbarItems = {}
        self.toolbarLabels = []
        self.toolbar = None
        
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
        The Application just finished loading from the NIB file. We
        setup the main window (and create a toolbar).
        """
        pool = NSAutoreleasePool.alloc ().init ()
        
        # For each label in TOOLBAR_LABELS, create a toolbar item. We
        # keep track of those items by using the self.toolbarItems
        # dictionary.
        for label in TOOLBAR_LABELS:
            tbi = NSToolbarItem.alloc ().initWithItemIdentifier_ (label)
            
            # Hook the toolbar item to a routine in self.imageView. 
            # The routine has to have the same name as label.
            tbi.setAction_ (label)
            tbi.setTarget_ (self.imageView)
            
            # This is the label that will appear in the toolbar
            tbi.setLabel_ (label)
            
            # This is the label that will appear in the config panel
            tbi.setPaletteLabel_ (label)
            
            # Set the tooltip text
            tbi.setToolTip_ (label)
            
            # Setup the item's icon
            path = os.path.abspath (RESOURCES_PATH + '/' + label + '.tiff')
            image = NSImage.alloc ().initWithContentsOfFile_ (path)
            
            tbi.setImage_ (image)
            
            self.toolbarItems[label] = tbi
            self.toolbarLabels.append (label)
        
        # Add the two extra items we always want: flexible space 
        # and customize.
        self.toolbarLabels.append (NSToolbarFlexibleSpaceItemIdentifier)
        self.toolbarLabels.append (NSToolbarCustomizeToolbarItemIdentifier)
        
        # Now that we have created the necessary toolbar items, we 
        # can create the toolbar itself.
        self.toolbar = NSToolbar.alloc ().initWithIdentifier_ ('mainToolbar')
        
        self.toolbar.setDelegate_ (self)
        
        # make the toolbar configurable
        self.toolbar.setAllowsUserCustomization_ (True)
        self.toolbar.setAutosavesConfiguration_ (True)
        
        # attach the toolbar to the window
        self.mainWindow.setToolbar_ (self.toolbar)
        
        pool.release ()
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
        
        # Are we asked to check and see if a new version is out?
        if (PREFS['CheckForNewVersion']):
            # Yes. Start a new thread and do the chack. We should 
            # give the user the possibility to have the new version
            # downloaded automatically.
            v = VersionChecker ()
        return
    
    
    def toolbarDefaultItemIdentifiers_ (self, toolbar):
        """
        Create the default toolbar.
        """
        return (self.toolbarLabels)
    
    
    def toolbarAllowedItemIdentifiers_ (self, toolbar):
        """
        List all the allowed toolbar items.
        """
        items = self.toolbarItems.keys ()
        items.sort ()
        items.append (NSToolbarSeparatorItemIdentifier)
        items.append (NSToolbarSpaceItemIdentifier)
        items.append (NSToolbarFlexibleSpaceItemIdentifier)
        items.append (NSToolbarPrintItemIdentifier)
        items.append (NSToolbarShowColorsItemIdentifier)
        items.append (NSToolbarShowFontsItemIdentifier)
        items.append (NSToolbarCustomizeToolbarItemIdentifier)
        return (items)
    
    
    def toolbar_itemForItemIdentifier_willBeInsertedIntoToolbar_ (self, 
                                                                  toolbar, 
                                                                  identifier, 
                                                                  flag):
        """
        Given an identifier, return the corresponding toolbar item.
        """
        return (self.toolbarItems[identifier])
    
    
    def displayImage (self):
        """
        This method gets called by the active RequestHandler object
        as soon as it is done reading image data. This means that we
        can be confident that the current frame buffer (identified by
        self.curentFrame) is properly setup.
        """
        self.imageView.display (self.frameBuffers[self.currentFrame], 
                                self.currentFrame)
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
            for i in range (n, fbIndex + 1):
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
            self.infoPanel = InfoController.infoController (self, self.imageView)
            self.infoPanel.showWindow_ (self)
            # set the menu item title to "Hide..."
            sender.setTitle_ ('Hide Info Panel')
        return
    
    
    def infoWindowWillClose (self):
        """
        Called just before the infoWindow will close. It sets the 
        correct label for the corresponding menu item.
        """
        self.infoPanelMenuItem.setTitle_ ('Show Info Panel')
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
    
    
    def updateProgressInfo (self, statusText, progressPercent):
        """
        Update both the statusField at the bottom of the window and
        the progress bar/wheel (progressIndicator).
        
        progressPercent tells where to draw the progress bar. If it
        is equal to -1, then the progress bar should be undetermined.
        If it is equal to 2.0, then we should stop the animation
        """
        pool = NSAutoreleasePool.alloc().init()
        
        if (self.statusField.stringValue () != statusText):
            self.statusField.setStringValue_ (statusText)
        
        if (progressPercent < 0):
            if (not self.progressIndicator.isIndeterminate ()):
                self.progressIndicator.setIndeterminate_ (True)
            self.progressIndicator.startAnimation_ (self)
        elif (progressPercent <= 1.0):
            if (self.progressIndicator.isIndeterminate ()):
                self.progressIndicator.setIndeterminate_ (False)
            self.progressIndicator.incrementBy_ (progressPercent)
        else:
            if (not self.progressIndicator.isIndeterminate ()):
                self.progressIndicator.setDoubleValue_ (self.progressIndicator.minValue ())
                self.progressIndicator.setIndeterminate_ (True)
            self.progressIndicator.stopAnimation_ (self)
        self.progressIndicator.setNeedsDisplay_ (True)
        
        pool.release ()
        return
    





