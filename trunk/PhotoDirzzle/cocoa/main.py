import sys
import os
import objc
from AppKit import *
from PyObjCTools.NibClassBuilder import extractClasses
from PyObjCTools import AppHelper

extractClasses('MainMenu')

# Import all submodules,  to make sure all
# classes are known to the runtime
import AppDelegate
import SrcImageView
import DstImageView


AppHelper.runEventLoop()
