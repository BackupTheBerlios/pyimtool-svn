#
#  VersionChecker.py
#  PyImtool
#
#  Created by Francesco Pierfederici on Fri Jun 11 2004.
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




