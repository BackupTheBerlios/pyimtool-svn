#
#  HeaderController.py
#  PyImtool
#
#  Created by Francesco Pierfederici on Thu Jun 03 2004.
#  Copyright (c) 2004 Francesco Pierfederici. All rights reserved.
#
# globals and the like
from utilities import *


from PyObjCTools import NibClassBuilder
NibClassBuilder.extractClasses("HeaderPanel")


# Globals
EMPTY_HEADER = [{'headerKey': '',
                 'headerValue': '',
                 'headerComment': ''}]


# class defined in InfoPanel.nib
class HeaderController (NibClassBuilder.AutoBaseClass):
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
    
    def headerController (self, app, view):
        return (HeaderController.alloc ().init (app, view))
    
    headerController = classmethod (headerController)
    
    def init (self, app, view):
        self = self.initWithWindowNibName_ ("HeaderPanel")
        self.imageView = view
        self.appDelegate = app
        
        self.imageName = None
        self.imageTitle = None
        
        self.header = []
        
        # Notify self.imageView that we are active
        self.imageView.setHeaderPanel (self)
        
        # Fetch the current image path/name
        (self.imageName, 
            self.imageTitle) = self.imageView.getImageNameTitle ()
        
        if (not self.imageName or not self.imageTitle):
            self.imageName = 'N/A'
            self.imageTitle = 'N/A'
        
        self.fetchHeader ()
        
        super (HeaderController, self).init ()
        return (self)
    
    
    def awakeFromNib (self):
        self.retain ()
        
        # Setup the name and title fields
        self.setField ('name', self.imageName)
        self.setField ('title', self.imageTitle)
        return
    
    
    def windowWillClose_ (self, notification):
        # tell the main window to stop tracking the mouse.
        self.appDelegate.headerWindowWillClose ()
        self.imageView.headerWindowWillClose ()
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
        else:
            pass
        return
    
    
    def setHeader (self, header):
        self.header = header
        return
    
    
    def setImageName (self, imageName):
        self.imageName = imageName
        self.header = self.fetchHeader ()
        self.setField ('name', self.imageName)
        return
    
    
    def setImageTitle (self, imageTitle):
        self.imageTitle = imageTitle
        self.setField ('title', self.imageTitle)
        return
    
    
    def fetchHeader (self):
        """
        Invoke IMHEADER to get the header of self.imageName
        Return the new header.
        """
        if (self.imageName == 'N/A' or 
            self.imageTitle == 'N/A' or
            not PREFS['irafIntegration']):
            self.header = EMPTY_HEADER
            return
        
        # Init the header
        if (self.header and self.header != EMPTY_HEADER):
            self.header = EMPTY_HEADER
        
        # Create a temporary parameter file
        (fd, name) = tempfile.mkstemp (dir='/tmp', text=True)
        os.write (fd, IRAF_PAR['imheader'] % (self.imageName))
        os.close (fd)
        
        task = IRAF_TASK['imheader'] % (PREFS['irafRoot'],
                                        name)
        
        # Run the external process
        (childOut, childIn, childErr) = popen2.popen3 (task)
        
        # Wait for the process to terminate and fetch the process 
        # output.
        childIn.close ()
        err = childErr.read ()
        childErr.close ()
        out = childOut.readlines ()
        childOut.close ()
        
        # Check for errors
        if (err and not out):
            self.header = EMPTY_HEADER
            msg = 'IMHEADER returned an error: %s' % (err)
            answer = NSRunAlertPanel ('Error', 
                                      msg, 
                                      'OK', 
                                      None, 
                                      None)
        else:
            # parse the header data, if any
            for line in out:
                data = {}
                try:
                    (key, val_comm) = line.split ('=', 1)
                    data['headerKey'] = key.strip ()
                except:
                    # print ('WARNING: line "%s" is wrong!' % (line))
                    continue
                
                # keys must be *at most* 8 character long!
                if (len (data['headerKey']) > 8):
                    continue
                
                try:
                    (val, comm) = val_comm.split ('/', 1)
                    data['headerValue'] = val.strip ()
                    data['headerComment'] = comm.strip ()
                except:
                    # No comment, I guess
                    data['headerValue'] = val_comm.strip ()
                    data['headerComment'] = ''
                self.header.append (data)
        
        # Cleanup the temporary files
        try:
            os.remove (name)
        except:
            pass
        
        return
    
    
    def showHeader (self):
        """
        Cocoa Binding method.
        """
        if (not self.header):
            self.fetchHeader ()
        return (self.header)
    
    
    def valueForUndefinedKey_ (self, key):
        if (key == 'delegate'):
            return (self)
        return (None)







