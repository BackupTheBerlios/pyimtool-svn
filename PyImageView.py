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
        self.bitmap = ''
        self.image = ''
        self.frameBuffer = None
        self.infoPanel = None
        self.trackMouse = False
        self.transformation = NSAffineTransform.transform ()
        return
    
    
    def isFlipped (self):
        """
        Nasty trick: needed to make sure that our
        MyImageView is anchoered to the top left
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
    
    
    def display (self, frameBuffer):
        pool = NSAutoreleasePool.alloc().init()
        
        self.frameBuffer = frameBuffer
        
        if (VERBOSE):
            sys.stderr.write ("Resizing to %dx%d.\n" % (frameBuffer.width, frameBuffer.height))
        self.setFrameSize_ ((frameBuffer.width, frameBuffer.height))
        
        try:
            tempBitmap = NSBitmapImageRep.alloc().initWithBitmapDataPlanes_pixelsWide_pixelsHigh_bitsPerSample_samplesPerPixel_hasAlpha_isPlanar_colorSpaceName_bytesPerRow_bitsPerPixel_ (
                (frameBuffer.buffer, None, None, None, None), 
                frameBuffer.width, 
                frameBuffer.height,  
                frameBuffer.bitsPerSample, 
                frameBuffer.samplesPerPixel, 
                frameBuffer.hasAlpha, 
                frameBuffer.isPlanar, 
                frameBuffer.colorSpaceName, 
                frameBuffer.width, 
                frameBuffer.bitsPerSample * frameBuffer.samplesPerPixel)
        except:
            if (VERBOSE):
                sys.stderr.write ('Bitmap creation failed.\n')
            return
        
        if (self.bitmap):
            if (self.bitmap != tempBitmap):
                self.bitmap.release ()
                self.bitmap = tempBitmap
                self.bitmap.retain ()
                tempBitmap.release ()
                if (VERBOSE):
                    sys.stderr.write ('Rempving old bitmap.\n')
        else:
            self.bitmap = tempBitmap
            self.bitmap.retain ()
            tempBitmap.release ()
            if (VERBOSE):
                sys.stderr.write ('No previous bitmap.\n')
        
        try:
            tempImage = NSImage.alloc ().init ()
        except:
            if (VERBOSE):
                sys.stderr.write ('Image creation failed.\n')
            return
        
        if (self.image):
            if (self.image != tempImage):
                self.image.release ()
                self.image = tempImage
                self.image.retain ()
                tempImage.release ()
                if (VERBOSE):
                    sys.stderr.write ('Rempving old image.\n')
        else:
            self.image = tempImage
            self.image.retain ()
            tempImage.release ()
            if (VERBOSE):
                sys.stderr.write ('No previous image.\n')
        
        self.image.addRepresentation_ (self.bitmap)
        
        self.setImage_ (self.image)
        self.setNeedsDisplay_ (True)
        
        pool.release ()
        return
    
    
    def mouseMoved_ (self, event):
        if (not self.trackMouse or not (self.frameBuffer and self.frameBuffer.buffer)):
            return
        
        (x, y) = self.convertPoint_fromView_ (event.locationInWindow (), None)
                
        frame = self.frame ()
        
        view_rect = self.superview ().frame ()
        view_rect = self.convertRect_fromView_ (view_rect, self.superview ())
        
        if (self.mouse_inRect_ ((x, y), frame) and 
            self.mouse_inRect_ ((x, y), view_rect)):
            
            x /= self.frameBuffer.zoom
            y /= self.frameBuffer.zoom
            
            try:
                (self.sx, self.sy) = wcsCoordTransform (self.frameBuffer.ct, x, y)
            except:
                print ('PYIMTOOL: *** coord. transform failed ***')
                self.sx = x + 1
                self.sy = y + 1
            
            # we want x and y to start from (0.5, 0.5)
            self.sy -= 1
            
            try:
                self.infoPanel.setField ('x', self.sx)
                self.infoPanel.setField ('y', self.sy)
            except:
                print ('ops!')
                pass
            
            i = int (x) + int (self.frameBuffer.imgWidth) * int (y)
            
            z1 = min (self.frameBuffer.ct.z1, self.frameBuffer.ct.z2)
            z2 = max (self.frameBuffer.ct.z1, self.frameBuffer.ct.z2)
            
            try:
                v = wcsPixTransform (self.frameBuffer.ct, self.frameBuffer.buffer[i])
            except:
                print ('PYIMTOOL: *** array index out of bounds ***')
                v = 0
            
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
            try:
                self.infoPanel.setField ('x', '---')
                self.infoPanel.setField ('y', '---')
                self.infoPanel.setField ('int', '---')
            except:
                pass
            self.sx = None
            self.sy = None
        return
    
    
    def startTrackingMouse (self, panel):
        """
        Strats treacking the mouse and updates the cursor fields in 
        the info window.
        """
        self.infoPanel = panel
        self.trackMouse = True
        
        if (self.frameBuffer and self.frameBuffer.buffer):
            # set the name, title and extension fields
            self.infoPanel.setField ('name', self.frameBuffer.wcs)
            self.infoPanel.setField ('title', self.frameBuffer.ct.imTitle)
            
            print (self.frameBuffer.wcs)
            print (self.frameBuffer.ct.imTitle)
        return
    
    
    def stopTrackingMouse (self):
        """
        Stops treacking the mouse.
        """
        self.trackMouse = False
        return







