#
#  PyOpenGLView.py
#  PyImtool
#
#  Created by Francesco Pierfederici on Thu Jun 03 2004.
#  Copyright (c) 2004 Francesco Pierfederici. All rights reserved.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

from utilities import *
from OpenGL import *
from OpenGL.GL import *
# from OpenGL.GLU import *


NibClassBuilder.extractClasses ("MainMenu")


# class defined in MainMenu.nib
class PyOpenGLView (NibClassBuilder.AutoBaseClass):
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
        
        # Since we only have one IRAF framebuffer, we should disable 
        # the "prev" and "next" buttons.
        self.window = self.window ()
        self.enablePrevButton = False
        self.enableNextButton = False
        
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
        
        self.offset = 0.
        self.scale = 1.
        return
    
    
    def free (self):
        pool = NSAutoreleasePool.alloc ().init ()
        for image in self.images.values ():
            if (image):
                image.release ()
        for frameBuffer in self.frameBuffers.values ():
            if (frameBuffer):
                del (frameBuffer)
        super (PyOpenGLView, self).free (self)
        pool.release ()
        return
    
    
    def initWithFrame_(self, frame):
        """
        Set th epixel format
        """
        print ('pixel format')
        attribs = [
            NSOpenGLPFANoRecovery,
            NSOpenGLPFAWindow,
            NSOpenGLPFAAccelerated,
            NSOpenGLPFADoubleBuffer,
            NSOpenGLPFAColorSize, 8,
            NSOpenGLPFAAlphaSize, 1,
            NSOpenGLPFADepthSize, 8,
            NSOpenGLPFAStencilSize, 1,
            NSOpenGLPFAAccumSize, 0,
        ]
        fmt = NSOpenGLPixelFormat.alloc().initWithAttributes_(attribs)
        self = super(PyOpenGLView, self).initWithFrame_pixelFormat_(frame, fmt)
        return self
    
    
    def prepareOpenGL (self):
        """
        OpenGL initialization routine
        """
        # setup the LUT
        lutData = file ('/Users/fpierfed/Desktop/heat.lut').readlines ()
        self.i2r = numarray.zeros (shape=(256), type='Float32')
        self.i2g = numarray.zeros (shape=(256), type='Float32')
        self.i2b = numarray.zeros (shape=(256), type='Float32')
        for i in range (len (lutData)):
            (r, g, b) = lutData[i].split ()
            self.i2r[i] = float (r)
            self.i2g[i] = float (g)
            self.i2b[i] = float (b)
        
        # Setup the OpenGL maps
        glPixelTransferf (GL_ALPHA_SCALE, 0.0)
        glPixelTransferf (GL_ALPHA_BIAS,  1.0)
        glPixelStorei (GL_UNPACK_ALIGNMENT, 1)
        
        glPixelMapfv (GL_PIXEL_MAP_I_TO_R, self.i2r)
        glPixelMapfv (GL_PIXEL_MAP_I_TO_G, self.i2g)
        glPixelMapfv (GL_PIXEL_MAP_I_TO_B, self.i2b)
        glPixelMapfv (GL_PIXEL_MAP_I_TO_A, 1)
        
        glPixelTransferi (GL_INDEX_SHIFT, 0)
        glPixelTransferi (GL_INDEX_OFFSET, 0)
        glPixelTransferi (GL_MAP_COLOR, GL_TRUE)
        glDisable (GL_DITHER)
        
        # clear color for the view
        glClearColor (0.0, 0.0, 0.0, 0.0)
        glClearDepth (1.0)
        
        # sstart with a fresh id matrix
        glLoadIdentity ()
        
        # clear the view
        glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glFlush ()
        return
    
    
    def validateToolbarItem_ (self, item):
        # This NEEDS to be implemented better!!!!!
        if (item.label () == "prev" and 
            not self.enablePrevButton):
            return (False)
        if (item.label () == "next" and 
            not self.enableNextButton):
            return (False)
        return (True)
    
    
    def isFlipped (self):
        """
        Bummer: the OpenGL view apparently needs to be "unflipped"
        otherwise the ScrollView it is contained in screws up scrolling.
        Of course, this means that the OpenGL view is anchored to the
        bottol-left corner of the ScrollView.
        """
        return (False)
    
    
    def acceptsFirstResponder (self):
        self.window.makeFirstResponder_ (self)
        return (True)
    
    
    def becomeFirstResponder (self):
        self.window.setAcceptsMouseMovedEvents_ (True)
        return (True)
    
    
    def resignFirstResponder (self):
        self.window.setAcceptsMouseMovedEvents_ (False)
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
        
        Each PyOpenGLView instance keeps a cache of images to display 
        (self.images). This cache is implemented as an array whose
        indices are the IDs (0 to N) of the images themselves.
        
        There is also an additional hash table (self.mapping) which 
        associates image IDs to IRAF framebuffer IDs (1 to N).
        
        At any time, there is always one extra image not associated to
        any IRAF framebuffer. That image is the hotSpare and is 
        initialized to None.
        
        Every time a PyOpenGLView instance is asked to display a new
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
        
        # Depending on self.frameNo, we might have to enable/disable
        # the prev/next button.
        if (self.frameNo == 1 and self.enablePrevButton):
            self.enablePrevButton = False
        elif (self.frameNo > 1 and not self.enablePrevButton):
            self.enablePrevButton = True
        
        # Start off by updating self.frameBuffers
        # HANDLE IT BETTER!!!!!
        self.frameBuffers[self.hotSpareID] = frameBuffer
        self.images[self.hotSpareID] = True
        
        # update the mapping, if needed
        if (self.mapping.has_key (self.frameNo)):
            # We are writing into an existing IRAF framebuffer
            
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
            # We have to create a new IRAF framebuffer
            
            # update the mapping
            self.mapping[self.frameNo] = self.hotSpareID
            
            # update the hotSpare ID
            self.hotSpareID = len (self.images.keys ())
            
            # create a new hotSpare
            self.images[self.hotSpareID] = None
            self.frameBuffers[self.hotSpareID] = None
        
        self.setFrameSize_ ((frameBuffer.width, frameBuffer.height))
        
        self.setNeedsDisplay_ (True)
        pool.release ()
        return
    
    
    def reshape (self):
        """ 
        Sets the receiver's viewport and coordinate system to reflect
        changes to the visible portion of the view.
        """
        visibleRect = self.visibleRect ()
        superVisibleRect = visibleRect
        
        # Conversion captures any scaling in effect
        superVisibleRect = self.convertRect_toView_ (superVisibleRect, 
                                                    self.superview ())
        
        self.openGLContext ().makeCurrentContext ()
        
        # Setup some basic OpenGL stuff
#         glPixelStorei (GL_UNPACK_ALIGNMENT, 1)
#         glTexEnvi (GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
#         glClearColor (0.0, 0.0, 0.0, 1.0)
#         glColor4f (1.0, 1.0, 1.0, 1.0)
#         glEnable (GL_BLEND)
#         glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
#         glDisable (GL_TEXTURE_RECTANGLE_EXT)
#         glEnable (GL_TEXTURE_2D)
        
        # Optimization: discard texture pixels that are too transparent
#         glEnable (GL_ALPHA_TEST)
#         glAlphaFunc (GL_GREATER, 0.05)
        
        glMatrixMode (GL_PROJECTION)
        glLoadIdentity ()
        glMatrixMode (GL_MODELVIEW)
        glLoadIdentity ()
        
        # reset the viewport to new dimensions
        glViewport (0, 0, 
                    int (superVisibleRect.size.width),
                    int (superVisibleRect.size.height))
        glOrtho (NSMinX (visibleRect), 
                 NSMaxX (visibleRect), 
                 NSMinY(visibleRect),
                 NSMaxY(visibleRect), 
                 -1.0, 1.0);
        
        self.setNeedsDisplay_ (True)
        return
    
    
    def drawRect_ (self, rect):
        """
        Draw the content of the PyOpenGLView instance on screen.
        
        We override this method in order to draw on screen using Quartz
        2D directly.
        """
        frame = self.mapping[self.frameNo]
        if (not self.frameBuffers[frame] or 
            not self.frameBuffers[frame].raw):
            return
        
        # now = time.time ()
        
        zoom = self.frameBuffers[frame].zoom
        
        # set the view port
        x = int (rect.origin.x)
        y = int (rect.origin.y)
        w = int (rect.size.width)
        h = int (rect.size.height)
        
        # Handle the zoom information
        zx = int (rect.origin.x / zoom)
        zy = int (rect.origin.y / zoom)
        zw = int (rect.size.width / zoom)
        zh = int (rect.size.height / zoom)
        
        endX = int (zx + zw)
        endY = int (zy + zh)
        
        (maxX, maxY) = self.frameBuffers[frame].buffer.shape
        if (endX > maxX):
            endX = maxX - 1
            zw = endX - zx
            print ('zx out of range')
        if (endY > maxY):
            endY = maxY - 1
            zh = endY - zy
            print ('zy out of range')
        
        # extract the affected pixels from the image buffer. we 
        # implement zoom by extracting as few pixels as possible.
        # this means that if zoom < 1, we extract one pixel every
        # 1/zoom pixels (stride=1/zoom). If zoom >= 1, we extract
        # all the pixels in the affected area (stride=1).
        # t0 = time.time ()
        if (zoom >= 1):
            raw = self.frameBuffers[frame].buffer[zy:endY,zx:endX].tostring ()
        else:
            stride = int (1. / zoom)
            raw = self.frameBuffers[frame].buffer[zy:endY:stride,zx:endX:stride].tostring ()
        # dt = time.time () - t0
        # print ('tostring() took %.02fs' % (dt))
        
        # draw the pixels
        # t0 = time.time ()
        if (zoom >= 1):
            glViewport (zx, zy, zw, zh)
            glPixelZoom (zoom, zoom)
            glDrawPixels (zw, 
                          zh, 
                          GL_COLOR_INDEX, 
                          GL_UNSIGNED_BYTE, 
                          raw)
        else:
            glViewport (x, y, w, h)
            glDrawPixels (w, 
                          h, 
                          GL_COLOR_INDEX, 
                          GL_UNSIGNED_BYTE, 
                          raw)
        glFlush ()
        # dt = time.time () - t0
        # print ('glDrawPixels() took %.02fs' % (dt))
        
        # dt = time.time () - now
        # print ('drawRect() took %.02fs' % (dt))
        return
    
    
    def mouseMoved_ (self, event):
        # Get the currently displayed image/frameBuffer
        imageID = self.mapping[self.frameNo]
        frameBuffer = self.frameBuffers[imageID]
        image = self.images[imageID]
        
        if (not self.trackMouse or not (frameBuffer and frameBuffer.raw)):
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
            
            # factor the zoom in computing the coordinate
            zoom = frameBuffer.zoom
            x /= zoom
            y /= zoom
            
            try:
                (self.sx, self.sy) = wcsCoordTransform (frameBuffer.ct, x, y)
            except:
                print ('PYIMTOOL: *** coord. transform failed ***')
                print (self.sx, self.sy)
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
            
            # i = int (x) + int (frameBuffer.imgWidth) * int (y)
            
            z1 = min (frameBuffer.ct.z1, frameBuffer.ct.z2)
            z2 = max (frameBuffer.ct.z1, frameBuffer.ct.z2)
            
            try:
                v = wcsPixTransform (frameBuffer.ct, frameBuffer.buffer[int (x), int (y)])
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
    
    
    def mouseDragged_ (self, event):
        """
        Implement color stretching by modifying the LUT
        """
        (x, y) = event.locationInWindow ()
        
        (w, h) = self.visibleRect ().size
        self.offset = x / w
        self.scale = (y - h / 2.) / h * MAX_CONTRAST * 2.
        
        # Modify a copy of the actual color tables
        i2r = (self.i2r * self.scale) + self.offset
        i2g = (self.i2g * self.scale) + self.offset
        i2b = (self.i2b * self.scale) + self.offset
        
        # Install the new color tables
        glPixelMapfv (GL_PIXEL_MAP_I_TO_R, i2r)
        glPixelMapfv (GL_PIXEL_MAP_I_TO_G, i2g)
        glPixelMapfv (GL_PIXEL_MAP_I_TO_B, i2b)
        
        self.setNeedsDisplay_ (True)
        return
    
    
    def keyDown_ (self, event):
        if (not self.reqHandler):
            print (1)
            return
        
        if (self.sx != None and self.sy != None):
            mods = event.modifierFlags ()
            if (mods == 256):
                # remember that the image is flipped vertically
                imageID = self.mapping[self.frameNo]
                height = self.frameBuffers[imageID].height
                
                key = event.characters ()[0]
                # update the RequestHandlerClass fields
                self.reqHandler.x = self.sx
                self.reqHandler.y = height - self.sy
                self.reqHandler.key = key
                self.reqHandler.frame = self.frameNo
                self.reqHandler.gotKey = True
                self.reqHandler = None
        else:
            sys.stderr.write ('no self.sx and/or no self.sy\n')
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
            
            if (frameBuffer and frameBuffer.raw):
                # set the name, title and extension fields
                self.infoPanel.setField ('name', frameBuffer.ct.ref)
                self.infoPanel.setField ('title', frameBuffer.ct.imTitle)
        return
    
    
    def stopTrackingMouse (self, panel=False):
        """
        Stops treacking the mouse.
        
        Remember that we might be in cursor mode 
        (self.reqHandler != None).
        """
        if (not self.reqHandler):
            self.trackMouse = False
        return
    
    
    def setImage_ (self, image):
        """
        Call drawRect_ () ro update the visibleRect of the OpenGL view.
        """
        self.drawRect_ (self.visibleRect ())
        return
    
    
    def zoomIn (self):
        # Get the currently displayed image/frameBuffer
        imageID = self.mapping[self.frameNo]
        frameBuffer = self.frameBuffers[imageID]
        image = self.images[imageID]
        
        if (not frameBuffer or not image):
            return
        
        (w0, h0) = (frameBuffer.width, frameBuffer.height)
        
        # update the zoom factor
        frameBuffer.zoom *= 2.0
        
        # resize the frame
        self.transformation.scaleBy_ (2.0)
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
        
        # update the zoom factor
        frameBuffer.zoom /= 2.0
        
        # resize the frame
        self.transformation.scaleBy_ (0.5)
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
        
        # resize the frame
        self.transformation = NSAffineTransform.transform ()
        self.transformation.scaleBy_ (frameBuffer.zoom)
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
        
        # update the zoom factor
        frameBuffer.zoom = 1.0
        
        # resize the frame
        self.transformation = NSAffineTransform.transform ()
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
                self.frameNo = newFrameNo
                self.setImage_ (self.images[imageID])
                # self.setNeedsDisplay_ (True)
        
        # update the state of teh next/prev buttons
        if (newFrameNo == 1):
            self.enablePrevButton = False
        else:
            self.enablePrevButton = True
        if (newFrameNo == len (self.mapping.keys ())):
            self.enableNextButton = False
        else:
            self.enableNextButton = True
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
                self.frameNo = newFrameNo
                self.setImage_ (self.images[imageID])
                # self.setNeedsDisplay_ (True)
        
        # update the state of teh next/prev buttons
        if (newFrameNo == 1):
            self.enablePrevButton = False
        else:
            self.enablePrevButton = True
        if (newFrameNo == len (self.mapping.keys ())):
            self.enableNextButton = False
        else:
            self.enableNextButton = True
        return







