#
#  PyImageView.py
#  PyImtool
#
#  Created by Francesco Pierfederici on Thu Jun 03 2004.
#  Copyright (c) 2004 Francesco Pierfederici. All rights reserved.
#
from utilities import *
from PyImage import *


# class defined in MainMenu.nib
class PyImageView (NSImageView):
    # the actual base class is NSImageView
    # The following outlets are added to the class:
    
    bitmap = ''
    image = ''
    
    def awakeFromNib (self):
        return
    
    
    def isFlipped (self):
        """
        Nasty trick: needed to make sure that our
        MyImageView is anchoered to the top left
        corner of the parent NSScrollView.
        See http://www.omnigroup.com/mailman/archive/macosx-dev/2003-October/036608.html
        """
        return (YES)
    
    
    def display (self, img):
        pool = NSAutoreleasePool.alloc().init()
        
        if (VERBOSE):
            sys.stderr.write ("Resizing to %dx%d.\n" % (img.width, img.height))
        self.setFrameSize_ ((img.width, img.height))
        
        try:
            tempBitmap = NSBitmapImageRep.alloc().initWithBitmapDataPlanes_pixelsWide_pixelsHigh_bitsPerSample_samplesPerPixel_hasAlpha_isPlanar_colorSpaceName_bytesPerRow_bitsPerPixel_ (
                (img.data, None, None, None, None), 
                img.width, 
                img.height,  
                img.bitsPerSample, 
                img.samplesPerPixel, 
                img.hasAlpha, 
                img.isPlanar, 
                img.colorSpaceName, 
                img.bytesPerRow, 
                img.bitsPerSample * img.samplesPerPixel)
        except:
            if (VERBOSE):
                sys.stderr.write ('Bitmap creation failed.\n')
            return (1)
        
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
            return (2)
        
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
        self.setNeedsDisplay_ (YES)
        
        pool.release ()
        return (0)
    
    








