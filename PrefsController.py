#
#  PrefController.py
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

# globals and the like
from utilities import *


from PyObjCTools import NibClassBuilder
NibClassBuilder.extractClasses("Preferences")



# class defined in Preferences.nib
class PrefsController (NibClassBuilder.AutoBaseClass):
    # the actual base class is WSWindowController
    # The following outlets are added to the class:
    # inetSockets
    # unixSockets
    # imageScale
    
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
    
    def prefsController (self):
        return (PrefsController.alloc ().init ())
    
    prefsController = classmethod (prefsController)
    
    def init (self):
        self = self.initWithWindowNibName_ ("Preferences")
        
        super (PrefsController, self).init ()
        return (self)
    
    
    def awakeFromNib (self):
        self.retain()
        
        # check the preferences and set the check-boxes
        # accordingly.
        if (PREFS['EnableIRAFIntegration']):
            self.irafIntegration.setState_ (NSOnState)
        else:
            self.irafIntegration.setState_ (NSOffState)
        
        self.imageScale.deselectAllCells ()
        if (PREFS['ScaleToFit']):
            self.imageScale.selectCellAtRow_column_ (1, 0)
        else:
            self.imageScale.selectCellAtRow_column_ (0, 0)
        
        if (PREFS['CheckForNewVersion']):
            self.versionCheck.setState_ (NSOnState)
        else:
            self.versionCheck.setState_ (NSOffState)
        
        return
    
    
    def checkBoxSelected_ (self, sender):
        # update our internal preference dictionary
        # with the new values
        try:
            state = sender.state ()
        except:
            pass
        nthreads = 0
        value = None
        
        if (sender == self.irafIntegration):
            key = 'EnableIRAFIntegration'
        elif (sender == self.imageScale):
            # self.imageScale is a NSMatrix. The first
            # is for "actual_size" behaviour, the second
            # is for "zoom_to_fit"
            value = sender.selectedRow ()
            key = 'ScaleToFit'
        else:
            return
        
        # determine the value
        if (value == None):
            if (state == NSOnState or state == NSMixedState):
                value = 1
            else:
                value = 0
        
        # update our internal preferences dictionary
        PREFS[key] = value
        
        return
    
    
    def windowShouldClose_ (self, sender):
        # save the preferences on file
        prefs = NSUserDefaults.standardUserDefaults ()
        for key in PREFS.keys ():
            # update the application preferences
            prefs.setBool_forKey_ (PREFS[key], key)
        # and acknowledge the fact that, now, we have a 
        # preferences file!
        prefs.setBool_forKey_ (True, 'HasPrefsFile')
        return (True)
    
    
    def windowWillClose_ (self, notification):
        self.autorelease()
        
        return











