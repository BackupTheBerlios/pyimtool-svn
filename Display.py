#
#  Display.py
#  pyimtool3
#
#  Created by Francesco Pierfederici on Thu Jun 03 2004.
#  Copyright (c) 2004 __MyCompanyName__. All rights reserved.
#
#!/usr/bin/python

import socket, os, string, sys
import Image, array
from utilities import *




def displayRaster (dataPlanes, 
    title, 
    width, 
    height,
    bitsPerSample, 
    samplesPerPixel, 
    isPlanar, 
    hasAlpha, 
    colorSpaceName, 
    bytesPerRow, 
    fileName=None):
    """Display an image using PyImtool.
    
    Input:
        fileName    the name of the image to display
                    if not None, it overrides dataPlanes.
        
        dataPlanes  a tuple of 5 array.arrays of type 'B'.
                    Each array holds the raster to display.
                    if isPlanar=True, then each array is 
                    assumed to hold data for a separate 
                    channel (e.g. R, G, B). If a coverage 
                    plane is present, it has to precede the 
                    other 4. If any of the arrays is empty, 
                    set it to None.
                    If isPlanar=False, then only the first 
                    plane is read. The raster is assumed to be 
                    in meshed configuration.
        
        isPlanar    see the discussion for dataPlanes.
    
    Output:
        N/A
    """
    pkt = initPacket ()
    
    # guess the siwe of the data buffers
    if (not isPlanar):
        # we care only about the firs plane
        





def displayFile (fileName):
    return




def initPacket ():
    packet = {'command': 'display',
        'title': '', 
        'width': 0, 
        'height': 0, 
        'bitsPerSample': 0, 
        'samplesPerPixel': 0, 
        'isPlanar': True, 
        'hasAlpha': False, 
        'colorSpaceName': '', 
        'bytesPerRow': 0, 
        'fileName': '', 
        'type': 'B', 
        'length': 0}
    return (packet)


def sendPacket (pkt, port=5137):
    exclude = ('command', 
        'type', 
        'length', 
        '<HEADER>', 
        '</HEADER>', 
        '<DATA>', 
        '</DATA>')
    
    # guess the right port to use
    if (not port):
        try:
            PORT = int (os.environ['IMTDEV'])
        except:
            PORT = 5137
    else:
        PORT = port
    
    # connect
    try:
        s = connect ('127.0.0.1', PORT)
    except:
        return (1)
    
    # compose the packet
    try:
        packet = str (pkt['command']) + '\n'
        packet += '<HEADER>\n'
        for key in pkt.keys ():
            if (key not in exclude):
                packet += key + ' = ' + str (pkt[key]) + '\n'
        packet += '</HEADER>\n'
        packet += '<DATA>\n'
        packet += 'type = ' + str (pkt['type']) + '\n'
        packet += 'length = ' + str (pkt['length']) + '\n'
        packet += pkt['data']
    except:
        return (2)
    
    # send the packet
    s.send (packet)
    
    # read the reply
    response = s.recv (max_size)
    
    # disconnect
    err = disconnect (s)
    
    if (not response):
        return (3)
    
    result = parse_packet (response)
    
    print (result)
    return (0)


