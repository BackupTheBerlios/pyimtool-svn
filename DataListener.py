#
#  DataListener.py
#  PyImtool
#
#  Created by Francesco Pierfederici on Thu Jun 03 2004.
#  Copyright (c) 2004 Francesco Pierfederici. All rights reserved.
#

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
        sock_type='inet', controller=None):
        """
        Constructor, setting initial variable values. Basically, we 
        open sockets and start listening to them.
        """
        threading.Thread.__init__(self, name=name)
        
        self.stop = False
        self.sleep = 1.0
        
        self.sock_type = sock_type
        if (sock_type == 'inet'):
            self.socket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
            s_address = (HOST, PORT)
        else:
            self.socket = socket.socket (socket.AF_UNIX, socket.SOCK_STREAM)
            s_address = UNIX_ADDR
            
        # allow reuse of the socket
        self.socket.setsockopt (socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind the socket and start listening
        self.socket.bind (s_address)
        self.socket.listen (NCONNECTIONS)
        
        # attach a RequestHandler to the server
        self.RequestHandlerClass = RequestHandler
        
        # attach the interface controller class
        self.controller = controller
        return
    
    
    def handle_request (self):
        """
        Handles incoming connections, one at the time. We simply do an
        accept on the socket/pipe. This means that we block until we 
        get data.
        
        Once we get data, we create a RequestHandler object and pass
        control to it.
        """
        try:
            (request, client_address) = self.socket.accept ()
        except socket.error:
            # Error handling goes here.
            sys.stderr.write ('PYIMTOOL: error opening the connection.\n')
            for exctn in sys.exc_info():
                print (exctn)
            return
        
        try:
            self.RequestHandlerClass (request, client_address, self)
        except:
            # Error handling goes here.
            sys.stderr.write ('PYIMTOOL: error handling the request.')
            for exctn in sys.exc_info ():
                print (exctn)
            return
        return
    
    
    def run (self):
        """
        Overload of threading.thread.run() main control loop.
        """
        try:
            while (not self.stop):
                self.handle_request ()
        finally:
            self.socket.close ()
        return
    
    
    def join (self, timeout=None):
        """
        Overrides the default join () method by closing any open 
        connection.
        """
        self.socket.close ()
        if (self.sock_type == 'unix'):
            try:
                os.remove (UNIX_ADDR)
            except:
                sys.stderr.write ('PYIMTOOL: *** failed to cleanup the pipe ' + UNIX_ADDR + ' ***')
        
        self.stop = True
        threading.Thread.join (self, timeout)
        return



