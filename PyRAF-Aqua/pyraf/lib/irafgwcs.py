"""irafgwcs.py: WCS handling for graphics

This contains some peculiar code to work around bugs in splot (and
possibly other tasks) where the WCS for an existing plot gets changed
before the plot is cleared.  I save the changed wcs in self.pending and
only commit the change when it appears to really be applicable.

$Id: irafgwcs.py,v 1.1 2003/10/08 18:33:13 dencheva Exp $
"""

import struct, Numeric, math
from irafglobals import IrafError

WCS_SLOTS = 16
WCS_RECORD_SIZE = 22  # (in 2 byte integers)
LINEAR = 0
LOG = 1
ELOG = 2 # ??? won't implement, for now
DEFINED = 1
CLIP = 2 # needed for this?
NEWFORMAT = 4

class IrafGWcs:

    """Class to handle the IRAF Graphics World Coordinate System
    Structure"""

    def __init__(self, arg=None):
        self.wcs = None
        self.pending = None
        self.set(arg)

    def commit(self):
        if self.pending:
            self.wcs = self.pending
            self.pending = None

    def clearPending(self):
        self.pending = None

    def __nonzero__(self):
        self.commit()
        return self.wcs is not None

    def set(self, arg=None):
        """Set wcs from metacode stream"""
        if arg is None:
            # commit immediately if arg=None
            self.wcs = _setWCSDefault()
            self.pending = None
            #print "Default WCS set for plotting window. Plot may not display properly."
            return
        wcsStruct = arg[1:]
        if arg[0] != len(wcsStruct):
            raise IrafError("Inconsistency in length of WCS graphics structure")
        self.pending = [None]*WCS_SLOTS
        for i in xrange(WCS_SLOTS):
            record = wcsStruct[WCS_RECORD_SIZE*i:WCS_RECORD_SIZE*(i+1)]
            # read 8 4 byte floats from beginning of record
            fvals = Numeric.fromstring(record[:8*2].tostring(),Numeric.Float32)
            # read 3 4 byte ints after that
            ivals = Numeric.fromstring(record[8*2:].tostring(),Numeric.Int32)
            self.pending[i] = tuple(fvals) + tuple(ivals)
        if self.wcs is None:
            self.commit()

    def pack(self):

        """Return the WCS in the original IRAF format"""

        self.commit()
        wcsStruct = Numeric.zeros(WCS_RECORD_SIZE * WCS_SLOTS, Numeric.Int16)
        for i in xrange(WCS_SLOTS):
            x = self.wcs[i]
            farr = Numeric.array(x[:8],Numeric.Float32)
            iarr = Numeric.array(x[8:],Numeric.Int32)
            wcsStruct[WCS_RECORD_SIZE*i:
                      WCS_RECORD_SIZE*(i+1)] = \
                      Numeric.fromstring(farr.tostring() + iarr.tostring(),
                                                             Numeric.Int16)
        return wcsStruct.tostring()


    def transform(self, x, y, wcsID):

        """Transform x,y to wcs coordinates for the given
        wcs (integer 0-16) and return as a 2-tuple"""

        self.commit()
        if wcsID == 0: return (x, y, wcsID)

        # Since transformation is defined by a direct linear (or log) mapping
        # between two rectangular windows, apply the usual linear
        # interpolation.

        # log scale does not affect the w numbers at all, a plot
        # ranging from 10 to 10,000 will have wx1,wx2 = (10,10000),
        # not (1,4)

        return (self.transform1d(coord=x,dimension='x',wcsID=wcsID),
                        self.transform1d(coord=y,dimension='y',wcsID=wcsID),
                        wcsID)

    def transform1d(self, coord, dimension, wcsID):

        wx1, wx2, wy1, wy2, sx1, sx2, sy1, sy2, xt, yt, flag = \
                 self.wcs[wcsID-1]
        if dimension == 'x':
            w1,w2,s1,s2,type = wx1,wx2,sx1,sx2,xt
        elif dimension == 'y':
            w1,w2,s1,s2,type = wy1,wy2,sy1,sy2,yt
        if (s2-s1) == 0.:
            raise IrafError("IRAF graphics WCS is singular!")
        fract = (coord-s1)/(s2-s1)
        if type == LINEAR:
            val = (w2-w1)*fract + w1
        elif type == LOG:
            lw2, lw1 = math.log10(w2), math.log10(w1)
            lval = (lw2-lw1)*fract + lw1
            val = 10**lval
        else:
            raise IrafError("Unknown or unsupported axis plotting type")
        return val

    def _isWcsDefined(self, i):

        w = self.wcs[i]
        if w[-1] & NEWFORMAT:
            if w[-1] & DEFINED: return 1
            else: return 0
        else:
            if w[4] or w[5] or w[6] or w[7]: return 0
            else: return 1

    def get(self, x, y, wcsID=None):

        """Returned transformed values of x, y using given wcsID or
        closest WCS if none given.  Return a tuple (wx,wy,wnum) where
        wnum is the selected WCS (0 if none defined)."""

        self.commit()
        if wcsID is None:
            wcsID = self._getWCS(x,y)
        return self.transform(x,y,wcsID)

    def _getWCS(self, x, y):

        """Return the WCS (16 max possible) that should be used to
        transform x and y. Returns 0 if no WCS is defined."""

        # The algorithm for determining which of multiple wcs's
        # should be selected is thus (and is different in one
        # respect from the IRAF cl):
        #
        # 1 determine which viewports x,y fall in
        # 2 if more than one, the tie is broken by choosing the one
        #   whose center is closer.
        # 3 in case of ties, the higher number wcs is chosen.
        # 4 if inside none, the distance is computed to the nearest part
        #   of the viewport border, the one that is closest is chosen
        # 5 in case of ties, the higher number wcs is chosen.

        indexlist = []
        # select subset of those wcs slots which are defined
        for i in xrange(len(self.wcs)):
            if self._isWcsDefined(i):
                indexlist.append(i)
        # if 0 or 1 found, we're done!
        if len(indexlist) == 1:
            return indexlist[0]+1
        elif len(indexlist) == 0:
            return 0
        # look for viewports x,y is contained in
        newindexlist = []
        for i in indexlist:
            x1,x2,y1,y2 = self.wcs[i][4:8]
            if (x1 <= x <= x2) and (y1 <= y <= y2):
                newindexlist.append(i)
        # handle 3 cases
        if len(newindexlist) == 1:
            # unique, so done
            return newindexlist[0]+1
        # have to find minimum distance either to centers or to edge
        dist = []
        if len(newindexlist) > 1:
            # multiple, find one with closest center
            for i in newindexlist:
                x1,x2,y1,y2 = self.wcs[i][4:8]
                xcen = (x1+x2)/2
                ycen = (y1+y2)/2
                dist.append((xcen-x)**2 + (ycen-y)**2)
        else:
            # none, now look for closest border
            newindexlist = indexlist
            for i in newindexlist:
                x1,x2,y1,y2 = self.wcs[i][4:8]
                xdelt = min([abs(x-x1),abs(x-x2)])
                ydelt = min([abs(y-y1),abs(y-y2)])
                if x1 <= x <= x2:
                    dist.append(ydelt**2)
                elif y1 <= y <= y2:
                    dist.append(xdelt**2)
                else:
                    dist.append(xdelt**2 + ydelt**2)
        # now return minimum distance viewport
        # reverse is used to give priority to highest WCS value
        newindexlist.reverse()
        dist.reverse()
        minDist = min(dist)
        return newindexlist[dist.index(minDist)]+1


def _setWCSDefault():
    """Define default WCS for STDGRAPH plotting area."""
    # set 8 4 byte floats
    farr = Numeric.array([0.,1.,0.,1.,0.,1.,0.,1.],Numeric.Float32)
    # set 3 4 byte ints
    iarr = Numeric.array([LINEAR,LINEAR,CLIP+NEWFORMAT],Numeric.Int32)
    wcsarr = tuple(farr)+tuple(iarr)

    wcs = []
    for i in xrange(WCS_SLOTS):
        wcs.append(wcsarr)

    return wcs
