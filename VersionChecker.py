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
        """
        Constructor
        
        Determine the name and version number of the current bundle.
        Also builds the NSURL object needed to check the update XML
        data (version.xml).
        """
        self.name = os.path.basename (sys.argv[0])
        self.version = NSBundle.mainBundle ().infoDictionary ()['CFBundleVersion']
        
        self.url = NSURL.URLWithString_ (HOME_PAGE + '/version.xml')
        
        # Do the actual check
        self.check ()
        return
    
    
    def check (self):
        """
        Check and see if the internet connection is up and, if so, 
        fetch the version.xml file. version.xml tells us which one is
        the latest available version. It is stored on the PyImtool
        Home Page (HOME_PAGE global variable) as HOME_PAGE/version.xml
        
        version.xml has potentially lists latest release number and
        download URL for several packages. Each package name is the 
        value of a <key> element of the main <dict>.
        
        Each package has a <dict> associated to it with two keys. One
        is the release number ('version') the other is the download URL
        ('url').
        """
        # Retrieve the version.xml file from the remote site. If the
        # connection is down (or the file is not there), an exception
        # is raised and we simply abort the check.
        try:
            updateData = NSDictionary.dictionaryWithContentsOfURL_ (self.url)
        except:
            updateData = None
        
        # If everything went well, let's try and extract the relevant 
        # information from the XML file. If our package is not listed
        # or if the 'version' and/or 'url' kers are not valid, we 
        # simply abort.
        if (updateData):
            latestVersion = updateData[self.name]['version']
            downloadURL = updateData[self.name]['url']
        else:
            latestVersion = None
            downloadURL = None
            print ('Update check failed.')
        
        # Do we have the latest version number and, if so, is it 
        # different from our version?
        if (latestVersion and 
            latestVersion != self.version):
            answer = NSRunAlertPanel ('A new version is available', 
                                      'A new version of %s is available (version %s). Would you like to download the new version now?' % (self.name, self.version), 
                                      'Yes', 
                                      'No', 
                                      None)
            
            # The user clicked 'Yes': open the downloadURL in the 
            # default web browser.
            if (NSOKButton == answer):
                NSWorkspace.sharedWorkspace ().openURL_ (NSURL.URLWithString_ (downloadURL))
        else:
            print ('Your copy of %s is up to date (version %s).' % (self.name, self.version))
        return












