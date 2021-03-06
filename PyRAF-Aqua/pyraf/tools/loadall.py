#! /usr/bin/env python

"""loadall.py: Load all the main packages in IRAF with verbose turned on

$Id: loadall.py,v 1.1 2003/10/08 18:42:10 dencheva Exp $
"""

import sys, traceback
from pyraf import iraf

iraf.setVerbose()

def printcenter(s, length=70, char="-"):
    l1 = (length-len(s))/2
    l2 = length-l1-len(s)
    print l1*char, s, l2*char

ptried = {}
npass = 0
ntotal = 0
plist = iraf.getPkgList()
keepGoing = 1
while keepGoing and (ntotal<len(plist)):
    plist.sort()
    nnew = 0
    npass = npass + 1
    printcenter("pass "+`npass` + " trying " +
            `len(plist)`, char="=")
    for pkg in plist:
        if not ptried.has_key(pkg):
            ptried[pkg] = 1
            nnew = nnew+1
            l1 = (70-len(pkg))/2
            l2 = 70-l1-len(pkg)
            printcenter(pkg)
            if pkg == "digiphotx":
                print """
                        Working around bug in digiphotx.
                        It screws up subsequent loading of digiphot tasks.
                        (It happens in IRAF too.)"""
            else:
                try:
                    iraf.load(pkg)
                except KeyboardInterrupt:
                    print 'Interrupt'
                    keepGoing = 0
                    break
                except Exception, e:
                    sys.stdout.flush()
                    traceback.print_exc()
                    if e.__class__ == MemoryError:
                        keepGoing = 0
                        break
                    print "...continuing...\n"
    ntotal = ntotal + nnew
    printcenter("Finished pass "+`npass` +
            " new pkgs " + `nnew` +
            " total pkgs " + `ntotal`, char="=")
    plist = iraf.getPkgList()
