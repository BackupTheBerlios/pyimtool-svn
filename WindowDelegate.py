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


NibClassBuilder.extractClasses("MainMenu")

# class defined in MainMenu.nib
class WindowDelegate (NibClassBuilder.AutoBaseClass):
    # the actual base class is NSObject
    # The following outlets are added to the class:
    # <none>
    def awakeFromNib (self):
        """
        Setup instance variables
        """
        self.snapsToEdges = True
        self.snapTolerance = 50.
        self.padding = 0.
        self.snapping = False
        
        # Register to receive notification NSWindowDidMoveNotification.
        # NSNotificationCenter.defaultCenter ().addObserver_selector_name_object_ (self, 
        #                                         'windowMoved', 
        #                                         NSWindowDidMoveNotification, 
        #                                         self.mainWindow)
        return
    
    
    def windowShouldClose_ (self, sender):
        NSApp ().terminate_ (self)
        return (YES)
    
    
    def windowMoved (self, notification):
        # Get some useful values
        myFrame = self.mainWindow.frame ()
        aPoint = myFrame.origin
        windowX = myFrame.origin.x
        windowY = myFrame.origin.y
        windowW = myFrame.size.width
        windowH = myFrame.size.height
        
        myScreenFrame = self.mainWindow.screen ().frame ()
        screenW = myScreenFrame.size.width
        screenH = myScreenFrame.size.height
        menuHeight = NSMenuView.menuBarHeight ()
        
        if (self.snapsToEdges and not self.snapping):
            self.snapping = True     # so we don't keep getting NSWindowDidMoveNotifications 
                                     # whilst we are snapping the window
            
            # Bottom of the screen
            if (windowY < self.snapTolerance):
                aPoint.y = 0 + self.padding
                self.springCoordinate (aPoint)
            
            # Left hand side of the screen */
            if (windowX < self.snapTolerance):
                aPoint.x = 0 + self.padding
                self.springCoordinate (aPoint)
            
            # Right hand side of the screen
            if (screenW - (windowW + windowX) < self.snapTolerance):
                aPoint.x = (screenW - windowW) - self.padding
                self.springCoordinate (aPoint)
            
            # Top of the screen
            if (screenH - menuHeight - (windowH + windowY) < self.snapTolerance):
                aPoint.y = (screenH - menuHeight - windowH) - self.padding
                self.springCoordinate (aPoint)
            
            # Add your custom logic here to deal with snapping to other edges,
            # such as the edges of other windows.
            
            # Suggestion for custom logic to deal with snapping to other windows:
            #     1. Get a list of your app's windows, other than this one.
            #     2. Ignore any that aren't of a type you want this window to snap to.
            #     3. Loop through them like this:
            #     3-1. Get the window's frame.
            #     3-2. Expand its frame by snapTolerance, using NSInsetRect(theWindowFrame, -snapTolerance, -snapTolerance).
            #     3-3. Check to see if this window's frame intersects with the expanded frame, using NSIntersectsRect()
            #     3-4. If so, do appropriate snapping.
            #     4. Optionally, continue looping through all other windows and do appropriate snapping similarly. */
            
            self.snapping = False
        return
    
    
    # Helper methods
    def springCoordinate (self, newOrigin):
        print ('spring', newOrigin)
        self.mainWindow.setFrameOrigin_ (newOrigin)
        return
    
    
    # Accessor methods
    def snapsToEdges (self):
        return (self.snapsToEdges)
    
    
    def setSnapsToEdges (self, flag):
        self.snapsToEdges = flag
        return
    
    
    def snapTolerance (self):
        return (self.snapTolerance)
    
    
    def setSnapTolerance (tolerance):
        self.snapTolerance = tolerance
        return
    
    
    def padding (self):
        return (self.padding)
    
    
    def setPadding (newPadding):
        self.padding = newPadding
        return
