#
#  PyRAF_AquaAppDelegate.py
#  PyRAF-Aqua
#
#  Created by Francesco Pierfederici on 8/14/04.
#  Copyright (c) 2004 __MyCompanyName__. All rights reserved.
#

from Foundation import NSLog
from PyObjCTools import NibClassBuilder

NibClassBuilder.extractClasses("MainMenu")
class PyRAF_AquaAppDelegate(NibClassBuilder.AutoBaseClass):    
    def applicationDidFinishLaunching_(self, aNotification):
        NSLog( "Application did finish launching." )
