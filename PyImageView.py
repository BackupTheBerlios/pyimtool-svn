#
#  PyImageView.py
#  PyImtool
#
#  Created by Francesco Pierfederici on Thu Jun 03 2004.
#  Copyright (c) 2004 Francesco Pierfederici. All rights reserved.
#
from utilities import *
from PyImage import *


NibClassBuilder.extractClasses ("MainMenu")


# class defined in MainMenu.nib
class PyImageView (NibClassBuilder.AutoBaseClass):
    # the actual base class is NSImageView
    # The following outlets are added to the class:
    def awakeFromNib (self):
        # self.images is the image cache. Every time we are asked to 
        # display an image in a (previously) empty IRAF framebuffer, 
        # we store the image in self.images. This allowes us to switch
        # between IRAF framebuffers very quickly.
        self.images = {0: None, 
                       1: None}
        
        # Each image in self.images has a framebuffer associated to it.
        self.frameBuffers = {0: None, 
                             1: None}
        
        # We have to have a way of associating images and IRAF 
        # frameBuffers. IRAF framebuffers start from 1 (and are 
        # specified by the user as second argument to the IRAF display
        # task). We start off with two IRAF framebuffers. The extra 
        # one (0) is the spare for double buffering. The mapping is
        # dynamic and is updated every time an IRAF display command is
        # issued. The image being displaied in the IRAF framebuffer n
        # is self.images[self.mapping[n]].
        self.mapping = {1: 1}
        
        # self.frameNo is the currently active IRAF framebuffer number.
        # At any time, the image currently being displied is
        # self.images[self.mapping[self.frameNo]].
        self.frameNo = 1
        self.hotSpareID = 0
        
        # Sometimes, we need a direct connection with the active 
        # RequestHandler instance
        self.reqHandler = None
        
        # Needed for imcursor type of requests
        self.sx = None
        self.sy = None
        
        self.infoPanel = None
        self.trackMouse = False
        self.magnifierActive = False
        self.transformation = NSAffineTransform.transform ()
        return
    
    def free (self):
        pool = NSAutoreleasePool.alloc ().init ()
        for image in self.images.values ():
            if (image):
                image.release ()
        for frameBuffer in self.frameBuffers.values ():
            if (frameBuffer):
                del (frameBuffer)
        super (PyImageView, self).free (self)
        pool.release ()
        return
    
    
    def isFlipped (self):
        """
        Nasty trick: needed to make sure that our
        MyImageView is anchored to the top left
        corner of the parent NSScrollView.
        See http://www.omnigroup.com/mailman/archive/macosx-dev/2003-October/036608.html
        """
        return (True)
    
    
    def acceptsFirstResponder (self):
        self.window ().makeFirstResponder_ (self)
        return (True)
    
    
    def becomeFirstResponder (self):
        self.window ().setAcceptsMouseMovedEvents_ (True)
        return (True)
    
    
    def resignFirstResponder (self):
        self.window ().setAcceptsMouseMovedEvents_ (False)
        return (True)
    
    
    def resetCursorRects (self):
        clipView = self.superview ()
        scrollView = self.superview ().superview ()
        frame = self.convertRect_fromView_ (clipView.frame (), scrollView)
        self.addCursorRect_cursor_ (frame, NSCursor.crosshairCursor ())
        return
    
    def getHotSpareID (self):
        return (self.hotSpareID)
    
    
    def setHotSpareID (self, newID):
        self.hotSpareID = newID
        return
    
    
    def setReqHandler (self, rh):
        self.reqHandler = rh
        
        # start tracking the mouse, even if the InfoPanel is closed.
        self.startTrackingMouse (panel=None)
        return
    
    
    def display (self, frameBuffer, frameID):
        """
        Build a new image based on the content of frameBuffer.
        
        Each PyImageView instance keeps a cache of images to display 
        (self.images). This cache is implemented as an array whose
        indices are the IDs (0 to N) of the images themselves.
        
        There is also an additional hash table (self.mapping) which 
        associates image IDs to IRAF framebuffer IDs (1 to N).
        
        At any time, there is always one extra image not associated to
        any IRAF framebuffer. That image is the hotSpare and is 
        initialized to None.
        
        Every time a PyImageView instance is asked to display a new
        image in a non empty IRAF framebuffer, we need to find out the
        ID of the hotSpare and compose the new image there. Then we 
        need to update the mapping to reflect the new image ID 
        associated to the relevant IRAF framebuffer. 
        
        The last step is to erase the previously active image and use
        it as the new hotSpare.
        
        N is the number of active IRAF framebuffers at any given time.
        """
        pool = NSAutoreleasePool.alloc().init()
        
        # AppDelegate internally indexes IRAF framebuffers starting 
        # from 0. We start from 1 to leave space for the initial 
        # hotSpare.
        self.frameNo = frameID + 1
        
        # Start off by updating self.frameBuffers
        # HANDLE IT BETTER!!!!!
        self.frameBuffers[self.hotSpareID] = frameBuffer
        
        # Create the bitmap
        try:
            bitmap = NSBitmapImageRep.alloc ()
            bitmap.initWithBitmapDataPlanes_pixelsWide_pixelsHigh_bitsPerSample_samplesPerPixel_hasAlpha_isPlanar_colorSpaceName_bytesPerRow_bitsPerPixel_ (
                (self.frameBuffers[self.hotSpareID].buffer, None, None, None, None), 
                 self.frameBuffers[self.hotSpareID].width, 
                 self.frameBuffers[self.hotSpareID].height,  
                 self.frameBuffers[self.hotSpareID].bitsPerSample, 
                 self.frameBuffers[self.hotSpareID].samplesPerPixel, 
                 self.frameBuffers[self.hotSpareID].hasAlpha, 
                 self.frameBuffers[self.hotSpareID].isPlanar, 
                 self.frameBuffers[self.hotSpareID].colorSpaceName, 
                 self.frameBuffers[self.hotSpareID].width, 
                 self.frameBuffers[self.hotSpareID].bitsPerSample * self.frameBuffers[self.hotSpareID].samplesPerPixel)
        except:
            if (VERBOSE):
                sys.stderr.write ('Bitmap creation failed.\n')
            return
        
        try:
            self.images[self.hotSpareID] = NSImage.alloc ().init ()
            self.images[self.hotSpareID].addRepresentation_ (bitmap)
        except:
            if (VERBOSE):
                sys.stderr.write ('Image creation failed.\n')
            return
        
        self.setFrameSize_ ((self.frameBuffers[self.hotSpareID].width, 
                             self.frameBuffers[self.hotSpareID].height))
        self.setImage_ (self.images[self.hotSpareID])
        self.setNeedsDisplay_ (True)
        
        # update the mapping, if needed
        if (self.mapping.has_key (self.frameNo)):
            # Remove the old image
            oldID = self.mapping[self.frameNo]
            
            # Remove the old image
            if (self.images[oldID]):
                del (self.images[oldID])
            
            # remove the old frameBuffer
            if (self.frameBuffers[oldID]):
                self.frameBuffers[oldID] = None
            
            # Update the mapping
            self.mapping[self.frameNo] = self.hotSpareID
            self.hotSpareID = oldID
        else:
            # update the mapping
            self.mapping[self.frameNo] = self.hotSpareID
            
            # update the hotSpare ID
            self.hotSpareID = len (self.images.keys ())
            
            # create a new hotSpare
            self.images[self.hotSpareID] = None
            self.frameBuffers[self.hotSpareID] = None
        pool.release ()
        return
    
    
    def mouseMoved_ (self, event):
        # Get the currently displayed image/frameBuffer
        imageID = self.mapping[self.frameNo]
        frameBuffer = self.frameBuffers[imageID]
        image = self.images[imageID]
        
        if (not self.trackMouse or not (frameBuffer and frameBuffer.buffer)):
            return
        
        (x, y) = self.convertPoint_fromView_ (event.locationInWindow (), None)
                
        frame = self.frame ()
        
        view_rect = self.superview ().frame ()
        view_rect = self.convertRect_fromView_ (view_rect, self.superview ().superview ())
        
        if (self.mouse_inRect_ ((x, y), frame) and 
            self.mouse_inRect_ ((x, y), view_rect)):
            if (self.infoPanel and not self.magnifierActive):
                self.infoPanel.enableMagnifier ()
                self.magnifierActive = True
            
            x /= frameBuffer.zoom
            y /= frameBuffer.zoom
            
            try:
                (self.sx, self.sy) = wcsCoordTransform (frameBuffer.ct, x, y)
            except:
                print ('PYIMTOOL: *** coord. transform failed ***')
                self.sx = x + 1
                self.sy = y + 1
            
            # we want x and y to start from (0.5, 0.5)
            self.sy -= 1
            
            if (self.infoPanel):
                try:
                    self.infoPanel.setField ('x', self.sx)
                    self.infoPanel.setField ('y', self.sy)
                except:
                    print ('ops!')
                    pass
            
            i = int (x) + int (frameBuffer.imgWidth) * int (y)
            
            z1 = min (frameBuffer.ct.z1, frameBuffer.ct.z2)
            z2 = max (frameBuffer.ct.z1, frameBuffer.ct.z2)
            
            try:
                v = wcsPixTransform (frameBuffer.ct, frameBuffer.buffer[i])
            except:
                print ('PYIMTOOL: *** array index out of bounds ***')
                v = 0
            
            if (self.infoPanel):
                try:
                    if (v >= z2):
                        self.infoPanel.setField ('int', unicode ("\263 %.4f" % (z2), 'mac_roman'))
                        return
                    if (v <= z1):
                        self.infoPanel.setField ('int', unicode ("\262 %.4f" % (z1), 'mac_roman'))
                        return
                    else:
                        self.infoPanel.setField ('int', "%.4f" % (v))
                        return
                except:
                    pass
        else:
            if (self.infoPanel):
                try:
                    self.infoPanel.setField ('x', '---')
                    self.infoPanel.setField ('y', '---')
                    self.infoPanel.setField ('int', '---')
                    if (self.magnifierActive):
                        self.infoPanel.disableMagnifier ()
                        self.magnifierActive = False
                except:
                    pass
            self.sx = None
            self.sy = None
        return
    
    
    def keyDown_ (self, event):
        if (not self.reqHandler):
            return
        
        if (self.sx != None and self.sy != None):
            mods = event.modifierFlags ()
            if (mods == 256):
                key = event.characters ()[0]
                # update the RequestHandlerClass fields
                self.reqHandler.x = self.sx
                self.reqHandler.y = self.sy
                self.reqHandler.key = key
                self.reqHandler.frame = self.frameNo
                self.reqHandler.gotKey = True
                self.reqHandler = None
        return
    
    
    def startTrackingMouse (self, panel):
        """
        Start treacking the mouse and updates the cursor fields in 
        the info window.
        
        If panel is None, simply activate mouse tracking but ignore
        the InfoPanel.
        """
        self.trackMouse = True
        
        if (panel):
            self.infoPanel = panel
            
            # Get the currently displayed image/frameBuffer
            imageID = self.mapping[self.frameNo]
            frameBuffer = self.frameBuffers[imageID]
            image = self.images[imageID]
            
            if (frameBuffer and frameBuffer.buffer):
                # set the name, title and extension fields
                self.infoPanel.setField ('name', frameBuffer.ct.ref)
                self.infoPanel.setField ('title', frameBuffer.ct.imTitle)
        return
    
    
    def stopTrackingMouse (self):
        """
        Stops treacking the mouse.
        """
        self.trackMouse = False
        return
    
    
    def zoomIn (self):
        # Get the currently displayed image/frameBuffer
        imageID = self.mapping[self.frameNo]
        frameBuffer = self.frameBuffers[imageID]
        image = self.images[imageID]
        
        if (not frameBuffer or not image):
            return
        
        (w0, h0) = (frameBuffer.width, frameBuffer.height)
        
        # setup the appropriate transformation
        self.transformation.scaleBy_ (2.0)
        
        # update the zoom factor
        frameBuffer.zoom *= 2.0
        
        # resize the frame
        newSize = self.transformation.transformSize_ ((w0, h0))
        self.setFrameSize_ (newSize)
        self.setNeedsDisplay_ (True)
        return
    
    
    def zoomOut (self):
        # Get the currently displayed image/frameBuffer
        imageID = self.mapping[self.frameNo]
        frameBuffer = self.frameBuffers[imageID]
        image = self.images[imageID]
        
        if (not frameBuffer or not image):
            return
        
        (w0, h0) = (frameBuffer.width, frameBuffer.height)
        
        # setup the appropriate transformation
        self.transformation.scaleBy_ (0.5)
        
        # update the zoom factor
        frameBuffer.zoom /= 2.0
        
        # resize the frame
        newSize = self.transformation.transformSize_ ((w0, h0))
        self.setFrameSize_ (newSize)
        self.setNeedsDisplay_ (True)
        return
    
    
    def zoomToFit (self):
        # Get the currently displayed image/frameBuffer
        imageID = self.mapping[self.frameNo]
        frameBuffer = self.frameBuffers[imageID]
        image = self.images[imageID]
        
        if (not frameBuffer or not image):
            return
        
        # get the min between the clip view dimensions
        (w, h) = self.superview ().frame ()[1]
        (w0, h0) = (frameBuffer.width, frameBuffer.height)
        
        # adjust the size if the scrollers are visible
        scrollView = self.superview ().superview ()
        hScroller = scrollView.horizontalScroller ()
        vScroller = scrollView.verticalScroller ()
        
        if (scrollView.hasHorizontalScroller () and h0 > h):
            h += NSScroller.scrollerWidthForControlSize_ (hScroller.controlSize ())
        if (scrollView.hasVerticalScroller () and w0 > w):
            w += NSScroller.scrollerWidthForControlSize_ (vScroller.controlSize ())
        
        # update the zoom factor
        if (w < h):
            # make sure the image width fits into the clip view
            frameBuffer.zoom = float (w) / float (w0)
        else:
            # make sure the image height fits into the clip view
            frameBuffer.zoom = float (h) / float (h0)
        
        # setup the appropriate transformation
        self.transformation = NSAffineTransform.transform ()
        self.transformation.scaleBy_ (frameBuffer.zoom)
        
        # resize the frame
        newSize = self.transformation.transformSize_ ((w0, h0))
        self.setFrameSize_ (newSize)
        self.setNeedsDisplay_ (True)
        return
    
    
    def actualSize (self):
        # Get the currently displayed image/frameBuffer
        imageID = self.mapping[self.frameNo]
        frameBuffer = self.frameBuffers[imageID]
        image = self.images[imageID]
        
        if (not frameBuffer or not image):
            return
        
        (w0, h0) = (frameBuffer.width, frameBuffer.height)
        
        # setup the appropriate transformation
        self.transformation = NSAffineTransform.transform ()
        
        # update the zoom factor
        frameBuffer.zoom = 1.0
        
        # resize the frame
        self.setFrameSize_ ((w0, h0))
        self.setNeedsDisplay_ (True)
        return
    
    
    def prev (self):
        """
        Display the image associated with the previous IRAF 
        framebuffer, if any.
        
        We need to update self.frameBuffers appropriately!
        """
        newFrameNo = self.frameNo - 1
        
        if (self.mapping.has_key (newFrameNo)):
            imageID = self.mapping[newFrameNo]
            
            if (self.images[imageID]):
                self.setImage_ (self.images[imageID])
                self.setNeedsDisplay_ (True)
                self.frameNo = newFrameNo
        return
    
    
    def next (self):
        """
        Display the image associated with the next IRAF 
        framebuffer, if any.
        
        We need to update self.frameBuffers appropriately!
        """
        newFrameNo = self.frameNo + 1
        
        if (self.mapping.has_key (newFrameNo)):
            imageID = self.mapping[newFrameNo]
            
            if (self.images[imageID]):
                self.setImage_ (self.images[imageID])
                self.setNeedsDisplay_ (True)
                self.frameNo = newFrameNo
        return







