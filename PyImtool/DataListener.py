#
#  DataListener.py
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
from RequestHandler import *
import threading



class DataListener (threading.Thread):
    """
    DataListener: a Thread class that listens to a socket/UNIX pipe 
    for incoming data. It uses the XImtool protocol for client/server
    communications.
    
    All the action is in the RequestHandler class: DataListener 
    simply sits on the socket/pipe waiting for incoming data. As soon
    as data comes though, a RequestHandler class is instantiated. The
    RequestHandler object handles the communication with the client
    and (of course) the decoding/encoding of the IIS packets.
    
    One side effect of this strategy is that connections are 
    stateless. Or, better yet, each connection is treated completely
    separately.
    """
    def __init__ (self, name='DataListener', addr=(HOST, PORT), 
        sockType='inet', controller=None):
        """
        Constructor, setting initial variable values. Basically, we 
        open sockets and start listening to them.
        """
        threading.Thread.__init__ (self, name=name)
        
        self.stop = False
        self.sleep = 1.0
        
        self.sockType = sockType
        if (sockType == 'inet'):
            self.socket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
            sockAddress = (HOST, PORT)
        else:
            self.socket = socket.socket (socket.AF_UNIX, socket.SOCK_STREAM)
            sockAddress = UNIX_ADDR
            
        # allow reuse of the socket
        self.socket.setsockopt (socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind the socket and start listening
        self.socket.bind (sockAddress)
        self.socket.listen (NCONNECTIONS)
        
        # attach a RequestHandler to the server
        self.RequestHandlerClass = RequestHandler
        
        # attach the interface controller class
        self.controller = controller
        return
    
    
    def handleRequest (self):
        """
        Handles incoming connections, one at the time. We simply do an
        accept on the socket/pipe. This means that we block until we 
        get data.
        
        Once we get data, we create a RequestHandler object and pass
        control to it.
        """
        try:
            (request, clientAddress) = self.socket.accept ()
        except socket.error:
            # Error handling goes here.
            sys.stderr.write ('PYIMTOOL: error opening the connection.\n')
            for exctn in sys.exc_info():
                print (str (exctn))
            return
        
        # We have data from the socket connection. Instantiate a 
        # RequestHandler object to take care of the communications 
        # with the client.
        self.RequestHandlerClass (request, clientAddress, self)
        try:
            pass
        except:
            # Error handling goes here.
            sys.stderr.write ('PYIMTOOL: error handling the request.')
            for exctn in sys.exc_info ():
                print (str (exctn))
            return
        return
    
    
    def run (self):
        """
        Overload of threading.thread.run() main control loop.
        """
        try:
            while (not self.stop):
                self.handleRequest ()
        finally:
            self.socket.close ()
        return
    
    
    def join (self, timeout=None):
        """
        Overrides the default join () method by closing any open 
        connection.
        """
        self.socket.close ()
        if (self.sockType == 'unix'):
            try:
                os.remove (UNIX_ADDR)
            except:
                sys.stderr.write ('PYIMTOOL: *** failed to cleanup the pipe ' + UNIX_ADDR + ' ***')
        
        self.stop = True
        threading.Thread.join (self, timeout)
        return



