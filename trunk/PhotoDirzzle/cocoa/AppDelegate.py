"""
AppDelegate.py
"""

import math

from PyObjCTools import NibClassBuilder, AppHelper
from objc import getClassList, objc_object
from AppKit import *
from Foundation import *

import numarray
import numarray.fft
import Image
import ImageChops



class AppDelegate(NibClassBuilder.AutoBaseClass):
    def awakeFromNib(self):
        self.alpha = round(self.alphaSlider.doubleValue() * 100.) / 100.
        self.srcData = None
        self.dstData = None
        self.invertDstImage = False
        
        self.alphaValueField.setStringValue_('%0.2f' % (self.alpha))
        
        # Register as a notification observer
        self.notificationCenter = NSNotificationCenter.defaultCenter()
        self.notificationCenter.addObserver_selector_name_object_ (self,
            'srcImageUpdated:', 'srcImageUpdated', None)
        return
    
    def alphaValueChanged_(self, sender):
        alpha = round(sender.doubleValue() * 100.) / 100.
        if(alpha != self.alpha):
            self.alpha = alpha
            self.alphaValueField.setStringValue_('%0.2f' % (self.alpha))
            
            # Get the src image
            image = self.srcImageView.image()
            
            if(image):
                # Sharpen the image and display the new one
                sharp = self.sharpenImage(image, self.alpha)
                self.updateDstImageView(sharp)
        return
    
    def srcImageUpdated_(self, notification):
        image = notification.object()
        
        # Sharpen the image and display the new one
        sharp = self.sharpenImage(image, self.alpha)
        self.updateDstImageView(sharp)
        return
    
    def updateDstImageView(self, imgData):
        # FIXME: support non grey-scale images as well
        img = Image.frombuffer('L', imgData.shape, imgData.tostring())
        if (self.invertDstImage):
            img = ImageChops.invert(img)
        img.transpose(Image.FLIP_TOP_BOTTOM).save('/tmp/pippo.tiff')
        
        newImage = NSImage.alloc().initWithContentsOfFile_('/tmp/pippo.tiff')
        if(newImage):
            self.dstImageView.setImage_(newImage)
        return
    
    def sharpenImage(self, image, alpha):
        # FIXME: support RGB images
        rep = image.representations()[0]
        height = rep.pixelsHigh()
        width = rep.pixelsWide()  
        samplesPerPixel = rep.samplesPerPixel()
        bytesPerRow = rep.bytesPerRow()
        bitmapData = rep.bitmapData()
    
        # Convert the image to a numarray array
        size = (width, height)
        
        imgData = numarray.fromstring(datastring=bitmapData,
                                      type=numarray.UInt8,
                                      shape=size)
        
        # Convert to double and do a FFT2D
        G = numarray.fft.fft2d(imgData.astype(numarray.Float64))
        
        # Compute the power spectrum
        SG = (numarray.abs(G)**2.) / (width * height)
        
        # KD = 0.14711
        D1 = (numarray.abs(SG)**(alpha / 2.))
        
        # Find the normalization constant KD by requiring ||D1|| <= 1
        firstPass = numarray.add.reduce(D1**2)
        norm = math.sqrt(numarray.add.reduce(firstPass))
        KD = 1. / norm
        D1 *= KD
        
        # Divide the fft by its power spectrum and go back to real space.
        F1 = G / D1
        f2 = numarray.fft.inverse_fft2d(F1).real
        
        # Bring f2 into the [0, 255] range
        min = f2.min()
        if (min != 0):
            f2 -= min
        
        max = f2.max()
        if (max != 0):
            f2 /= max
            f2 *= 255.
        return(f2.astype(numarray.UInt8))
    
    def invertDstImage_(self, sender):
        image = self.dstImageView.image()
        if(image):
            # Turn this NSImage into a PIL image and invert it
            rep = image.representations()[0]
            height = rep.pixelsHigh()
            width = rep.pixelsWide()  
            bitmapData = rep.bitmapData()
            img = Image.frombuffer('L', (width, height), bitmapData).transpose(Image.FLIP_TOP_BOTTOM)
            # Invert and save to a temp file
            ImageChops.invert(img).save('/tmp/pippo.tiff')
            
            # Update the destination NSImageView
            newImage = NSImage.alloc().initWithContentsOfFile_('/tmp/pippo.tiff')
            if(newImage):
                self.dstImageView.setImage_(newImage)
            
            self.invertDstImage = not self.invertDstImage
        return
    
    def windowShouldClose_(self, sender):
        NSApp().terminate_(self)
        return(True)







