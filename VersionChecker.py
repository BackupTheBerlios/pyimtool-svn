#
#  VersionChecker.py
#  PyImtool
#
#  Created by Francesco Pierfederici on Fri Jun 11 2004.
#  Copyright (c) 2004 Francesco Pierfederici. All rights reserved.
#

# globals and the like
from utilities import *




class VersionChecker (object):
    """
    Check and see if a new version is out.
    
    If this happens to be an old version, inform the user of the 
    availability of a more recent release and ask them is they want 
    to have it downloaded for them.
    
    If so, fetch the new release and display a dialog showing the 
    progress of the download. Once the download has finished, dismiss
    the progress bar and tell the user where the new file has been
    downloaded.
    """
    def __init__ (self):
        """Constructor"""
        pass




