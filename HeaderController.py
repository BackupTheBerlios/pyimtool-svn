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
        self.header = {}
        
        super (HeaderController, self).init ()
        return (self)
    
    
    def awakeFromNib (self):
        self.retain ()
        
        # Notify self.imageView that we are active
        self.imageView.setHeaderPanel (self)
        
        # Fetch the current image path/name
        (self.imageName, 
            self.imageTitle) = self.imageView.getImageNameTitle ()
        
        if (not self.imageName or not self.imageTitle):
            self.imageName = 'N/A'
            self.imageTitle = 'N/A'
        else:
            self.header = self.fetchHeader ()
        
        # Setup the name and title fields
        self.setField ('name', self.imageName)
        self.setField ('title', self.imageTitle)
        return
    
    
    def windowWillClose_ (self, notification):
        # tell the main window to stop tracking the mouse.
        self.appDelegate.headerWindowWillClose ()
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
        TASK = '/iraf/iraf/bin.macosx/x_images.e imheader'
        TEMPLATE = 'imheader.$nargs = 1\nimheader.images = "%s"\n'
        TEMPLATE += 'imheader.imlist = "*.imh,*.fits,*.pl,*.qp,*.hhh"\n'
        TEMPLATE += 'imheader.longheader = yes\n'
        TEMPLATE += 'imheader.userfields = yes\n'
        TEMPLATE += 'imheader.mode = "ql"\n'
        TEMPLATE += '# EOF\n'
        
        # Init the header
        header = {}
        
        # Create a temporary parameter file
        (fd, name) = tempfile.mkstemp (dir='/tmp', text=True)
        os.write (fd, TEMPLATE % (self.imageName))
        os.close (fd)
        
        TASK += ' @%s' % (name)
        
        # Run the external process
        (childOut, childIn, childErr) = popen2.popen3 (TASK)
        
        # Wait for the process to terminate and fetch the process 
        # output.
        childIn.close ()
        err = childErr.readlines ()
        childErr.close ()
        out = childOut.readlines ()
        childOut.close ()
        
        # parse the header data, if any
        for line in out:
            try:
                (key, val_comm) = line.split ('=', 1)
                key = key.strip ()
            except:
                # print ('WARNING: line "%s" is wrong!' % (line))
                continue
            
            try:
                (val, comm) = val_comm.split ('/', 1)
                val = val.strip ()
                comm = comm.strip ()
            except:
                # No comment, I guess
                val = val_comm.strip ()
                comm = ''
            header[key] = (val, comm)
        
        # Cleanup the temporary files
        try:
            os.remove (name)
        except:
            pass
        
        print (header)
        return (header)









