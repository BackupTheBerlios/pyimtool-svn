#
#  RequestHandler.py
#  PyImtool
#
#  Created by Francesco Pierfederici on Thu Jun 03 2004.
#  Copyright (c) 2004 Francesco Pierfederici. All rights reserved.
#

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
    def __init__ (self):
        """
        This is the class constructor. It is the Python constructor
        since we are actually instantiating this object ourselves.
        """
        self.needsUpdate = 0
        # these NEED to be set automatically from the client 
        # interaction
        self.width = None
        self.height = None
        self.frame = 0
        self.key = None
        self.x = 0
        self.y = 0
        self.y1 = -1
        self.sequence = -1
        self.gotKey = None
        return
    
    
    def decodeFrameNo (self, z):
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
        parses the wcsText and populates the fields 
        of a CoordTransf instance.
        we start from the CoordTransf of the input
        frame buffer, if any
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
            
            # determine the best formato for WCS output
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
        self.frame = self.decodeFrameNo (pkt.z & 07777) - 1
        
        # erase the frame buffer
        fb = self.server.controller.initFrame (self.frame)
        self.server.controller.currentFrame = self.frame
        return
    
    
    def handleLut (self, pkt):
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
                    sys.stderr.write (exctn + '\n')
            
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
                self.frame = self.decodeFrameNo (z) - 1
                
                if (self.frame > MAX_FRAMES):
                    sys.stderr.write ("PYIMTOOL: attempt to select non existing frame.\n")
                    return
                
                # init the framebuffer
                self.server.controller.initFrame (self.frame)
                
                return
            
            sys.stderr.write ("PYIMTOOL: unable to select a frame.\n")
            return
        
        sys.stderr.write ("PYIMTOOL: what shall I do?\n")
        return
        
    
    def handleWCS (self, pkt):
        if (pkt.tid & IIS_READ):
            # Return the WCS for the referenced frame.
            if ((pkt.x & 017777) and (pkt.y & 017777)):
                # return IIS version number
                text = "version=" + str (IIS_VERSION)
                text = rightPad (text, SZ_OLD_WCSBUF)
            else:
                frame  = self.decodeFrameNo (pkt.z & 0177777) - 1
                try:
                    fb = self.server.controller.fb[frame]
                except:
                    fb = None
                
                if ((pkt.x & 017777) and (pkt.t & 017777)):
                    self.frame = frame
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
            # Read the WCS infor from the client
            # frames start from 1, we start from 0
            self.frame = self.decodeFrameNo (pkt.z & 07777) - 1
            
            try:
                fb = self.server.controller.fb[self.frame]
            except:
                # the selected frame does not exist, create it
                fb = self.server.controller.initFrame (self.frame)
            
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
        return
    
    
    def handleMemory (self, pkt):
        if (pkt.tid & IIS_READ):
            pass
        else:
            # get the frame number, we start from 0
            self.frame = self.decodeFrameNo (pkt.z & 07777) - 1
            try:
                fb = self.server.controller.fb[self.frame]
            except:
                # the selected frame does not exist, create it
                fb = self.server.controller.initFrame (self.frame)
            
            # decode x and y
            self.x = pkt.x & XYMASK
            self.y = pkt.y & XYMASK
            
            # read the data
            tBytes = 0
            if (fb.width and fb.height):
                if (not self.needsUpdate):
                    del (fb.buffer)
                    fb.buffer = array.array ('B', ' ' * fb.width * fb.height)
                    self.needsUpdate = 1
                start = self.x + self.y * fb.width
                end = start + pkt.nbytes
                fb.buffer[start:end] = array.array ('B', pkt.datain.read (pkt.nbytes))
            else: 
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
                if (VERBOSE):
                    sys.stderr.write ('PYIMTOOL: saved y coordinate.\n')
            elif (not width):
                deltaY = self.y - self.y1
                fb.width = int (abs (len (data) / deltaY))
                # if we added a new fbconfigs entry, let's update
                # the value for the framebuffer width!
                if (fbconfigs.has_key (fb.config)):
                    fbconfigs[fb.config][1] = width
                if (VERBOSE):
                    sys.stderr.write ('PYIMTOOL: deltaX: ' + str (fb.width) + '\n')
        return
    
    
    def handleImcursor (self, pkt):
        done = 0
        
        if (pkt.tid & IIS_READ):
            if (pkt.tid & IMC_SAMPLE):
                # return the cursor position
                wcs = int (pkt.z)
                (sx, sy, key, frame) = self.server.controller.imgView.getCursor ()
                frame -= 1
                
                self.returnCursor (pkt.dataout, sx, sy, frame, wcs, '0', '')
            else:
                # wait until the user presses a key
                self.server.controller.imgView.reqHandler = self
                while (not done):
                    if (self.gotKey != None):
                        done = 1
                        self.gotKey = None
                    time.sleep (0.2)
                # <--- end of the while loop
                sx = self.x
                sy = self.y
                frame = self.frame
                key = self.key
                
                self.returnCursor (pkt.dataout, sx, sy, frame, 1, key, '')
        else:
            # read the cursor position in logical coordinates
            sx = int (pkt.x)
            sy = int (pkt.y)
            wx = float (pkt.x)
            wy = float (pkt.y)
            wcs = int (pkt.z)
            
            if (wcs):
                # decode thw WCS info for the current frame
                try:
                    fb = self.server.controller.fb[self.frame]
                except:
                    # the selected frame does not exist, create it
                    fb = self.server.controller.initFrame (self.frame)
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
                    sys.stderr.write (exctn + '\n')
            
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
                if (self.needsUpdate):
                    self.server.controller.animateProgressWeel ()
                    # self.updateScreen ()
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
                # sys.stderr.write ('no-op\n')
                pass
            
            if (not (packet.tid & IIS_READ)):
                # OK, discard the rest of the data
                nbytes = packet.nbytes
                while (nbytes > 0):
                    # for (nbytes = ndatabytes;  nbytes > 0;  nbytes -= n):
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
        if (self.needsUpdate):
            self.displayImage ()
        return
    
    
    def updateScreen (self):
        self.server.controller.updateProgressBar (10)
        return
    
    
    def displayImage (self, reset=1):
        # get rid of the progress bar
        # self.server.controller.updateProgressBar (100)
        
        try:
            fb = self.server.controller.fb[self.frame]
        except:
            # the selected frame does not exist, create it
            fb = self.server.controller.initFrame (self.frame)
        
        if (not fb.height):
            width = fb.width       
            height = int (len (fb.buffer) / width)
            fb.height = height
        
            # display the image
            if (len (fb.buffer) and height > 0):
                self.server.controller.display (self.frame, width, height, True)
        else:
            self.server.controller.display (self.frame, fb.width, fb.height, False)
        return

