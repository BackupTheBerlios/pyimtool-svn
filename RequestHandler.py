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
        This is the class constructor.
        """
        self.needs_update = 0
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
        self.got_key = None
        return
    
    
    def decode_frameno (self, z):
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
    
    
    def wcs_update (self, wcs_text, fb=None):
        """
        parses the wcs_text and populates the fields 
        of a coord_tran instance.
        we start from the coord_tran of the input
        frame buffer, if any
        """
        if (fb):
            ct = fb.ct
        else:
            ct = coord_tran ()
        if (not ct.valid):
            ct.zt = W_UNITARY
            
            # read wcs_text
            data = string.split (wcs_text, '\n')
            ct.imtitle = data[0]
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
                ct.imtitle = "[NO WCS]"
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
            
            # add_mapping, if we can
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
                fb.img_width = ct.dnx + 1   # for some reason, the width is always
                                            # 1 pixel smaller...
                fb.img_height = ct.dny
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
    
    
    def return_cursor (self, dataout, sx, sy, frame, wcs, key, strval=''):
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
        dataout.write (right_pad (curval, SZ_IMCURVAL))
        return
    
    
    def handle_feedback (self, pkt):
        self.frame = self.decode_frameno (pkt.z & 07777) - 1
        
        # erase the frame buffer
        fb = self.server.controller.init_frame (self.frame)
        self.server.controller.current_frame = self.frame
        return
    
    
    def handle_lut (self, pkt):
        if (pkt.subunit & COMMAND):
            data_type = str (pkt.nbytes / 2) + 'h'
            size = struct.calcsize (data_type)
            line = pkt.datain.read (pkt.nbytes)
            n = len (line)
            if (n < pkt.nbytes):
                return
            try:
                x = struct.unpack (data_type, line)
            except:
                for exctn in sys.exc_info():
                    print (exctn)
            
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
                self.frame = self.decode_frameno (z) - 1
                
                if (self.frame > MAX_FRAMES):
                    print ("PYIMTOOL: attempt to select non existing frame.")
                    return
                
                # init the framebuffer
                self.server.controller.init_frame (self.frame)
                
                return
            
            print ("PYIMTOOL: unable to select a frame.")
            return
        
        print ("PYIMTOOL: what shall I do?")
        return
        
    
    def handle_wcs (self, pkt):
        if (pkt.tid & IIS_READ):
            # Return the WCS for the referenced frame.
            if ((pkt.x & 017777) and (pkt.y & 017777)):
                # return IIS version number
                text = "version=" + str (IIS_VERSION)
                text = right_pad (text, SZ_OLD_WCSBUF)
            else:
                frame  = self.decode_frameno (pkt.z & 0177777) - 1
                try:
                    fb = self.server.controller.fb[frame]
                except:
                    fb = None
                
                if ((pkt.x & 017777) and (pkt.t & 017777)):
                    self.frame = frame
                    if (fb and fb.ct.a != None):
                        wcs = "%s\n%f %f %f %f %f %f %f %f %d\n" \
                            % (fb.ct.imtitle, fb.ct.a, fb.ct.b, fb.ct.c, fb.ct.d,
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
                    text = right_pad (text, SZ_WCSBUF)
                else:
                    if (frame < 0 or not fb or not len (fb.buffer)):
                        text = "[NOSUCHFRAME]"
                    else:
                        text = fb.wcs
                    
                    # old style or new style?
                    if ((pkt.x & 0777)):
                        text = right_pad (text, SZ_WCSBUF)
                    else:
                        text = right_pad (text, SZ_OLD_WCSBUF)
            pkt.dataout.write (text)
        else:
            # Read the WCS infor from the client
            # frames start from 1, we start from 0
            self.frame = self.decode_frameno (pkt.z & 07777) - 1
            
            try:
                fb = self.server.controller.fb[self.frame]
            except:
                # the selected frame does not exist, create it
                fb = self.server.controller.init_frame (self.frame)
            
            # set the width and height of the framebuffer
            fb_config = (pkt.t & 0777) + 1
            try:
                (nframes, fb.width, fb.height) = fbconfigs [fb_config]
            except:
                print ('PYIMTOOL: *** non existing framebuffer config (' + str (fb_config) + '). ***')
                print ('PYIMTOOL: *** adding a new framebuffer config (' + str (fb_config) + '). ***')
                fbconfigs [fb_config] = [1, None, None]
                fb.width = None
                fb.height = None
            
            # do we have to deal with the new WCS format? (not used, for now)
            new_wcs   = (pkt.x & 0777)
            
            # read the WCS info
            line = pkt.datain.read (pkt.nbytes)
            
            # paste it in the frame buffer
            fb.wcs = line
                        
            fb.ct.format = W_DEFFORMAT
            fb.ct.imtitle = ''
            fb.ct.valid = 0
            fb.ct = self.wcs_update (line, fb)
            
            return
        return
    
    
    def handle_memory (self, pkt):
        if (pkt.tid & IIS_READ):
            pass
        else:
            # get the frame number, we start from 0
            self.frame = self.decode_frameno (pkt.z & 07777) - 1
            try:
                fb = self.server.controller.fb[self.frame]
            except:
                # the selected frame does not exist, create it
                fb = self.server.controller.init_frame (self.frame)
            
            # decode x and y
            self.x = pkt.x & XYMASK
            self.y = pkt.y & XYMASK
            
            # read the data
            t_bytes = 0
            if (fb.width and fb.height):
                if (not self.needs_update):
                    del (fb.buffer)
                    fb.buffer = array.array ('B', ' ' * fb.width * fb.height)
                    self.needs_update = 1
                start = self.x + self.y * fb.width
                end = start + pkt.nbytes
                fb.buffer[start:end] = array.array ('B', pkt.datain.read (pkt.nbytes))
            else: 
                if (not self.needs_update):
                    # init the framebuffer
                    fb.buffer.fromstring (pkt.datain.read (pkt.nbytes))
                    fb.buffer.reverse ()
                    self.needs_update = 1
                else:
                    data = array.array ('B', pkt.datain.read (pkt.nbytes))
                    data.reverse ()
                    fb.buffer += data
            
            width = fb.width
            
            if (not width and self.y1 < 0):
                self.y1 = self.y
                if (VERBOSE):
                    print ('PYIMTOOL: saved y coordinate.')
            elif (not width):
                delta_y = self.y - self.y1
                fb.width = int (abs (len (data) / delta_y))
                # if we added a new fbconfigs entry, let's update
                # the value for the framebuffer width!
                if (fbconfigs.has_key (fb.config)):
                    fbconfigs[fb.config][1] = width
                if (VERBOSE):
                    print ('PYIMTOOL: delta_x: ' + str (fb.width))
        return
    
    
    def handle_imcursor (self, pkt):
        done = 0
        
        if (pkt.tid & IIS_READ):
            if (pkt.tid & IMC_SAMPLE):
                # return the cursor position
                wcs = int (pkt.z)
                (sx, sy, key, frame) = self.server.controller.imgView.get_cursor ()
                frame -= 1
                
                self.return_cursor (pkt.dataout, sx, sy, frame, wcs, '0', '')
            else:
                # wait until the user presses a key
                self.server.controller.imgView.req_handler = self
                while (not done):
                    if (self.got_key != None):
                        done = 1
                        self.got_key = None
                    time.sleep (0.2)
                # <--- end of the while loop
                sx = self.x
                sy = self.y
                frame = self.frame
                key = self.key
                
                self.return_cursor (pkt.dataout, sx, sy, frame, 1, key, '')
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
                    fb = self.server.controller.init_frame (self.frame)
                fb.ct = self.wcs_update (fb.wcs)
                if (fb.ct.valid):
                    if (abs (fb.ct.a) > 0.001):
                        sx = int ((wx - fb.ct.tx) / fb.ct.a)
                    if (abs (fb.ct.d) > 0.001):
                        sy = int ((wy - xt.ty) / fb.ct.d)
            cursor_x = sx
            cursor_y = sy
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
                print ('PYIMTOOL: error unpacking the data.')
                for exctn in sys.exc_info():
                    print (exctn)
            
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
                self.handle_feedback (packet)
            elif (packet.subunit077 == LUT):
                self.handle_lut (packet)
                # read the next packet
                line = packet.datain.read (size)
                n = len (line)
                continue
            elif (packet.subunit077 == MEMORY):
                self.handle_memory (packet)
                if (self.needs_update):
                    self.server.controller.animateProgressWeel ()
                    # self.update_screen ()
                # read the next packet
                line = packet.datain.read (size)
                n = len (line)
                continue
            elif (packet.subunit077 == WCS):
                self.handle_wcs (packet)
                line = packet.datain.read (size)
                n = len (line)
                continue
            elif (packet.subunit077 == IMCURSOR):
                self.handle_imcursor (packet)
                line = packet.datain.read (size)
                n = len (line)
                continue
            else:
                # print ('no-op')
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
        if (self.needs_update):
            self.display_image ()
        return
    
    
    def update_screen (self):
        self.server.controller.updateProgressBar (10)
        return
    
    
    def display_image (self, reset=1):
        # get rid of the progress bar
        # self.server.controller.updateProgressBar (100)
        
        try:
            fb = self.server.controller.fb[self.frame]
        except:
            # the selected frame does not exist, create it
            fb = self.server.controller.init_frame (self.frame)
        
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

