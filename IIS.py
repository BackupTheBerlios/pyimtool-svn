#
#  IIS.py
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

from utilities import *

class IIS (object):
    def __init__ (self, verbose=False):
        self.tid = None
        self.subunit = None
        self.subunit077 = None
        self.nbytes = None
        self.x = None
        self.y = None
        self.z = None
        self.t = None
        
        # Communication channels
        self.datain = None
        self.dataout = None
        
        # Debug info
        self.verbose = verbose
        self.f1 = file ('/tmp/fromClient.dat', 'ab')
        self.f2 = file ('/tmp/toClient.dat', 'ab')
        return
    
    
    def toClient (self, data):
        """
        Write "data" to the client using the active connection.
        """
        self.dataout.write (data)
        self.dataout.flush ()
        
        if (self.verbose):
            # sys.stderr.write ('toClient: %s\n' % (data))
            self.f2.write (data)
        return
    
    
    def fromClient (self, nBytes):
        """
        Read "nBytes" from the client using the active connection.
        """
        data = self.datain.read (nBytes)
        
        if (self.verbose):
            # sys.stderr.write ('fromClient: %s\n' % (data))
            self.f1.write (data)
        return (data)
    
    
    def __del__ (self):
        """Standard desctructor"""
        if (self.verbose):
            self.f1.close ()
            self.f2.close ()
        return




