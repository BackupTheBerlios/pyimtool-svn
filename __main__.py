#
#  __main__.py
#  pyimtool3
#
#  Created by Francesco Pierfederici on Thu Jun 03 2004.
#  Copyright (c) 2004 __MyCompanyName__. All rights reserved.
#

try:
    # scan for pth files that made it into the bundle
    import os, site
    site.addsitedir(os.path.dirname(os.path.realpath(__file__)))
except ImportError:
    pass

from PyObjCTools import AppHelper
from Foundation import NSProcessInfo

# import classes required to start application
import AppDelegate

# start the event loop
AppHelper.runEventLoop(argv=[])
