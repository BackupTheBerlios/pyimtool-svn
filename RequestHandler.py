#
#  RequestHandler.py
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
from IIS import *
import time



class RequestHandler (SocketServer.StreamRequestHandler):
    """
    This class does the actual work of parsing the incoming streams 
    and perform the necessary actions (display image, overlay regions
    and so on).
    
    The communication protocol used is IIS (XImtool).
    """
    def __init__ (self, request, clientAddress, server):
        """
        This is the class constructor. It is the Python constructor
        since we are actually instantiating this object ourselves.
        """
        self.needsUpdate = 0
        # these NEED to be set automatically from the client 
        # interaction
        self.width = None
        self.height = None
        self.frameNo = 0
        self.key = None
        self.x = 0
        self.y = 0
        self.y1 = -1
        self.sequence = -1
        self.gotKey = False
        
        SocketServer.StreamRequestHandler.__init__ (self, request, clientAddress, server)
        return
    
    
    def decodeFrameNo (self, z):
        """
        Given a IIS packet header key z, it decodes the frame number
        the client is interested in.
        """
        
        try:
            z = int (z)
        except:
            z = 1
        if (not z):
            z = 1
        n = 0                
        while (not (z & 1)):
            n += 1
            z >>= 1
        return (max (1, n + 1))
    
    
    def wcsUpdate (self, wcsText, fb=None):
        """
        Parses the wcsText and populates the fields of a CoordTransf
        instance. We start from the CoordTransf of the input 
        framebuffer, if any.
        """
        if (fb):
            ct = fb.ct
        else:
            ct = CoordTransf ()
        if (not ct.valid):
            ct.zt = W_UNITARY
            
            # read wcsText
            data = string.split (wcsText, '\n')
            ct.imTitle = data[0]
            # we are expecting 8 floats and 1 int
            try:
                (ct.a, ct.b, ct.c, ct.d, 
                 ct.tx, ct.ty, ct.z1, ct.z2, 
                 ct.zt) = string.split (data[1])
                ct.a = float (ct.a)
                ct.b = float (ct.b)
                ct.c = float (ct.c)
                ct.d = float (ct.d)
                ct.tx = float (ct.tx)
                ct.ty = float (ct.ty)
                ct.z1 = float (ct.z1)
                ct.z2 = float (ct.z2)
                ct.zt = int (ct.zt)
            except:
                ct.imTitle = "[NO WCS]"
                ct.a = 1
                ct.d = 1
                ct.b = 0
                ct.c = 0
                ct.tx = 0
                ct.ty = 0
                ct.zt = W_UNITARY
            ct.valid += 1
            
            # Determine the best format for WCS output.
            if (ct.valid and ct.zt == W_LINEAR):
                z1 = ct.z1
                z2 = ct.z2
                zrange = abs (z1 - z2)
                zavg = (abs (z1) + abs (z2)) / 2.0
                if (zrange < 100.0 and zavg < 200.0):
                    ct.format = " %7.2f %7.2f %7.3f%c"
                elif (zrange > 99999.0 or zavg > 99999.0):
                    ct.format = " %7.2f %7.2f %7.3g%c"
                else:
                    ct.format = W_DEFFORMAT
            else:
                ct.format = " %7.2f %7.2f %7.0f%c"
            
            # add mapping, if we can
            if (len (data) < 4):
                return (ct)
            
            # we are expecting 1 string, 2 floats, and 6 int
            try:
                (ct.region, ct.sx, ct.sy, ct.snx, 
                 ct.sny, ct.dx, ct.dy, ct.dnx, 
                 ct.dny) = string.split (data[2])
                ct.sx = float (ct.sx)
                ct.sy = float (ct.sy)
                ct.snx = int (ct.snx)
                ct.sny = int (ct.sny)
                ct.dx = int (ct.dx)
                ct.dy = int (ct.dy)
                ct.dnx = int (ct.dnx)
                ct.dny = int (ct.dny)
                ct.ref = string.strip (data[3])
                # if this works, we also have the real size of the image
                fb.imgWidth = ct.dnx + 1   # for some reason, the width is always
                                           # 1 pixel smaller...
                fb.imgHeight = ct.dny
            except:
                ct.region = 'none'
                ct.sx = 1.0
                ct.sy = 1.0
                ct.snx = fb.width
                ct.sny = fb.height
                ct.dx = 1
                ct.dy = 1
                ct.dnx = fb.width
                ct.dny = fb.height
                ct.ref = 'none'
        return (ct)
    
    
    def returnCursor (self, dataout, sx, sy, frame, wcs, key, strval=''):
        """
        writes the cursor position to dataout.
        input:
            dataout:    the output stream
            sx:         x coordinate
            sy:         y coordinate
            wcs:        nonzero if we want WCS translation
            frame:      frame buffer index
            key:        keystroke used as trigger
            strval:     optional string value
        """
        wcscode = (frame + 1) * 100 + wcs
        if (key == '\32'):
            curval = "EOF"
        else:
            if (key in string.printable and not key in string.whitespace):
                keystr = key
            else:
                keystr = "\\%03o" % (ord (key))
        
        # send the necessary infor to the client
        curval = "%10.3f %10.3f %d %s %s\n" % (sx, sy, wcscode, keystr, strval)
        dataout.write (rightPad (curval, SZ_IMCURVAL))
        return
    
    
    def handleFeedback (self, pkt):
        self.server.controller.updateProgressInfo ('Erasing current frame...', -1)
        
        self.frameNo = self.decodeFrameNo (pkt.z & 07777) - 1
        
        # erase the frame buffer
        fb = self.server.controller.initFrame (self.frameNo)
        self.server.controller.setCurrentFrame (self.frameNo)
        return
    
    
    def handleLut (self, pkt):
        self.server.controller.updateProgressInfo ('Choosing current frame...', -1)
        if (pkt.subunit & COMMAND):
            dataType = str (pkt.nbytes / 2) + 'h'
            size = struct.calcsize (dataType)
            line = pkt.datain.read (pkt.nbytes)
            n = len (line)
            if (n < pkt.nbytes):
                return
            try:
                x = struct.unpack (dataType, line)
            except:
                for exctn in sys.exc_info():
                    sys.stderr.write (exctn)
            
            if (len (x) < 14):
                # pad it with zeroes
                y = []
                for i in range (14):
                    try:
                        y.append (x[i])
                    except:
                        y.append (0)
                x = y
                del (y)
            
            if (len (x) == 14):
                z = int (x[0])
                # frames start from 1, we start from 0
                self.frameNo = self.decodeFrameNo (z) - 1
                
                if (self.frameNo > MAX_FRAMES):
                    raise (IndexError, 'frame index grated than maximum allowed (%d)' % (MAX_FRAMES))
                    return
                
                # init the framebuffer
                self.server.controller.initFrame (self.frameNo)
                return
            raise (SyntaxError, 'malformed packet header')
            return
        sys.stderr.write ("PYIMTOOL: what shall I do?\n")
        return
        
    
    def handleWCS (self, pkt):
        if (pkt.tid & IIS_READ):
            self.server.controller.updateProgressInfo ('Writing WCS to client...', -1)
            # Return the WCS for the referenced frame.
            if ((pkt.x & 017777) and (pkt.y & 017777)):
                # return IIS version number
                text = "version=" + str (IIS_VERSION)
                text = rightPad (text, SZ_OLD_WCSBUF)
            else:
                frame  = self.decodeFrameNo (pkt.z & 0177777) - 1
                try:
                    fb = self.server.controller.getFrame (frame)
                except:
                    fb = None
                
                if ((pkt.x & 017777) and (pkt.t & 017777)):
                    self.frameNo = frame
                    if (fb and fb.ct.a != None):
                        wcs = "%s\n%f %f %f %f %f %f %f %f %d\n" \
                            % (fb.ct.imTitle, fb.ct.a, fb.ct.b, fb.ct.c, fb.ct.d,
                            fb.ct.tx, fb.ct.ty, fb.ct.z1, fb.ct.z2, fb.ct.zt)
                    else:
                        wcs = "[NOSUCHWCS]\n"
                    if (fb and fb.ct.sx != None):
                        mapping = "%s %f %f %d %d %d %d %d %d\n%s\n" \
                            % (fb.ct.region, fb.ct.sx, fb.ct.sy, fb.ct.snx, fb.ct.sny, 
                            fb.ct.dx, fb.ct.dy, fb.ct.dnx, fb.ct.dny, fb.ct.ref)
                    else:
                        mapping = ""
                    text = wcs + mapping
                    text = rightPad (text, SZ_WCSBUF)
                else:
                    if (frame < 0 or not fb or not len (fb.buffer)):
                        text = "[NOSUCHFRAME]"
                    else:
                        text = fb.wcs
                    
                    # old style or new style?
                    if ((pkt.x & 0777)):
                        text = rightPad (text, SZ_WCSBUF)
                    else:
                        text = rightPad (text, SZ_OLD_WCSBUF)
            pkt.dataout.write (text)
        else:
            self.server.controller.updateProgressInfo ('Reading WCS from client...', -1)
            # Read the WCS infor from the client
            # frames start from 1, we start from 0
            self.frameNo = self.decodeFrameNo (pkt.z & 07777) - 1
            
            try:
                fb = self.server.controller.getFrame (self.frameNo)
            except:
                # the selected frame does not exist, create it
                fb = self.server.controller.initFrame (self.frameNo)
            
            # set the width and height of the framebuffer
            fbConfig = (pkt.t & 0777) + 1
            try:
                (nframes, fb.width, fb.height) = fbconfigs [fbConfig]
            except:
                sys.stderr.write ('PYIMTOOL: *** non existing framebuffer config (' + str (fbConfig) + '). ***\n')
                sys.stderr.write ('PYIMTOOL: *** adding a new framebuffer config (' + str (fbConfig) + '). ***\n')
                fbconfigs [fbConfig] = [1, None, None]
                fb.width = None
                fb.height = None
            
            # do we have to deal with the new WCS format? (not used, for now)
            newWCS   = (pkt.x & 0777)
            
            # read the WCS info
            line = pkt.datain.read (pkt.nbytes)
            
            # paste it in the frame buffer
            fb.wcs = line
                        
            fb.ct.format = W_DEFFORMAT
            fb.ct.imTitle = ''
            fb.ct.valid = 0
            fb.ct = self.wcsUpdate (line, fb)
        return
    
    
    def handleMemory (self, pkt):
        if (pkt.tid & IIS_READ):
            pass
        else:
            # get the frame number, we start from 0
            self.frameNo = self.decodeFrameNo (pkt.z & 07777) - 1
            try:
                fb = self.server.controller.getFrame (self.frameNo)
            except:
                # the selected frame does not exist, create it
                fb = self.server.controller.initFrame (self.frameNo)
            
            # decode x and y
            self.x = pkt.x & XYMASK
            self.y = pkt.y & XYMASK
            
            # read the data
            tBytes = 0
            if (fb.width and fb.height):
                # tell the controller (AppDelegate) to update the 
                # status info on the main window.
                totalSize = fb.width * fb.height
                self.server.controller.updateProgressInfo ('Reading pixel data...', 
                                                            float (pkt.nbytes) / float (totalSize))
                
                if (not self.needsUpdate):
                    del (fb.buffer)
                    fb.buffer = array.array ('B', ' ' * totalSize)
                    self.needsUpdate = 1
                start = self.x + self.y * fb.width
                end = start + pkt.nbytes
                fb.buffer[start:end] = array.array ('B', pkt.datain.read (pkt.nbytes))
            else: 
                # tell the controller (AppDelegate) to update the 
                # status info on the main window.
                totalSize = fb.width * fb.height
                self.server.controller.updateProgressInfo ('Reading pixel data...', -1)
                
                if (not self.needsUpdate):
                    # init the framebuffer
                    fb.buffer.fromstring (pkt.datain.read (pkt.nbytes))
                    fb.buffer.reverse ()
                    self.needsUpdate = 1
                else:
                    data = array.array ('B', pkt.datain.read (pkt.nbytes))
                    data.reverse ()
                    fb.buffer += data
            width = fb.width
            
            if (not width and self.y1 < 0):
                self.y1 = self.y
            elif (not width):
                deltaY = self.y - self.y1
                fb.width = int (abs (len (data) / deltaY))
                # if we added a new fbconfigs entry, let's update
                # the value for the framebuffer width!
                if (fbconfigs.has_key (fb.config)):
                    fbconfigs[fb.config][1] = width
        return
    
    
    def handleImcursor (self, pkt):
        if (pkt.tid & IIS_READ):
            self.server.controller.updateProgressInfo ('Cursor mode ON', 2)
            
            if (pkt.tid & IMC_SAMPLE):
                # return the cursor position
                # wcs = int (pkt.z)
                # (sx, sy, key, frame) = self.server.controller.imageView.getCursor ()
                # frame -= 1
                # 
                # self.returnCursor (pkt.dataout, sx, sy, frame, wcs, '0', '')
                print ('To be implemented.')
            else:
                # wait until the user presses a key
                self.server.controller.imageView.setReqHandler (self)
                
                while (not self.gotKey):
                    # Wait for the PyImageView instance to wake us up
                    time.sleep (0.3)
                
                # If we are here, it means that
                # 1. the user pressed a key whilst the cursor was 
                #    inside PyImageView
                # 2. PyImageView intercepted the keyDown event and
                #    notified us by setting our self.gotKey to True
                sx = self.x
                sy = self.y
                frame = self.frameNo
                key = self.key
                
                # Return the appropriate cursor values to the client
                self.returnCursor (pkt.dataout, sx, sy, frame, 1, key, '')
        else:
            self.server.controller.updateProgressInfo ('Reading cursor from client...', -1)
            # read the cursor position in logical coordinates
            sx = int (pkt.x)
            sy = int (pkt.y)
            wx = float (pkt.x)
            wy = float (pkt.y)
            wcs = int (pkt.z)
            
            if (wcs):
                # decode thw WCS info for the current frame
                try:
                    fb = self.server.controller.getFrame (self.frameNo)
                except:
                    # the selected frame does not exist, create it
                    fb = self.server.controller.initFrame (self.frameNo)
                fb.ct = self.wcsUpdate (fb.wcs)
                if (fb.ct.valid):
                    if (abs (fb.ct.a) > 0.001):
                        sx = int ((wx - fb.ct.tx) / fb.ct.a)
                    if (abs (fb.ct.d) > 0.001):
                        sy = int ((wy - xt.ty) / fb.ct.d)
            cursorX = sx
            cursorY = sy
        
        return
    
    
    def handle (self):
        """
        This is where the action starts.
        """
        self.server.controller.updateProgressInfo ('Idle.', 2)
        
        # create a packet structure
        packet = IIS ()
        packet.datain = self.rfile
        packet.dataout = self.wfile
                
        # decode the header
        size = struct.calcsize ('8h')
        line = packet.datain.read (size)
        n = len (line)
        if (n < size):
            return
        
        while (n):
            try:
                bytes = struct.unpack ('8h', line)
            except:
                sys.stderr.write ('PYIMTOOL: error unpacking the data.\n')
                for exctn in sys.exc_info():
                    sys.stderr.write (exctn)
            
            # verify checksum
            # DO SOMETHING!
            
            # decode the packet fields
            subunit = bytes[2]
            subunit077 = subunit & 077
            tid = bytes[0]
            x = bytes[4] & 0177777
            y = bytes[5] & 0177777
            z = bytes[6] & 0177777
            t = bytes[7] & 017777
            ndatabytes = - bytes[1]
            
            # are the bytes packed?
            if (not (tid & PACKED)):
                ndatabytes *= 2
            
            # populate the packet structure
            packet.subunit = subunit
            packet.subunit077 = subunit077
            packet.tid = tid
            packet.x = x
            packet.y = y
            packet.z = z
            packet.t = t
            packet.nbytes = ndatabytes
            
            # decide what to do, depending on the
            # value of subunit            
            if (packet.subunit077 == FEEDBACK):
                self.handleFeedback (packet)
            elif (packet.subunit077 == LUT):
                self.handleLut (packet)
                # read the next packet
                line = packet.datain.read (size)
                n = len (line)
                continue
            elif (packet.subunit077 == MEMORY):
                self.handleMemory (packet)
                # if (self.needsUpdate):
                #     self.server.controller.animateProgressWeel ()
                # read the next packet
                line = packet.datain.read (size)
                n = len (line)
                continue
            elif (packet.subunit077 == WCS):
                self.handleWCS (packet)
                line = packet.datain.read (size)
                n = len (line)
                continue
            elif (packet.subunit077 == IMCURSOR):
                self.handleImcursor (packet)
                line = packet.datain.read (size)
                n = len (line)
                continue
            else:
                # no-op
                pass
            
            if (not (packet.tid & IIS_READ)):
                # OK, discard the rest of the data
                nbytes = packet.nbytes
                while (nbytes > 0):
                    if (nbytes < SZ_FIFOBUF):
                        n = nbytes
                    else:
                        n = SZ_FIFOBUF
                    m = self.rfile.read (n)
                    if (m <= 0):
                        break
                    nbytes -= n
            
            # read the next packet
            line = packet.datain.read (size)
            n = len (line)
            if (n < size):
                return
        # <--- end of the while (n) loop
        self.server.controller.updateProgressInfo ('Done.', 2.0)
        
        if (self.needsUpdate):
            self.server.controller.displayImage ()
        return
    
    
    def returnCursor (self, dataout, sx, sy, frame, wcs, key, strval=''):
        """
        writes the cursor position to dataout.
        input:
            dataout:    the output stream
            sx:         x coordinate
            sy:         y coordinate
            wcs:        nonzero if we want WCS translation
            frame:      frame buffer index
            key:        keystroke used as trigger
            strval:     optional string value
        """
        wcscode = (frame + 1) * 100 + wcs
        if (key == '\32'):
            curval = "EOF"
        else:
            if (key in string.printable and not key in string.whitespace):
                keystr = key
            else:
                keystr = "\\%03o" % (ord (key))
        
        # send the necessary infor to the client
        curval = "%10.3f %10.3f %d %s %s\n" % (sx, sy, wcscode, keystr, strval)
        dataout.write (rightPad (curval, SZ_IMCURVAL))
        return ()





