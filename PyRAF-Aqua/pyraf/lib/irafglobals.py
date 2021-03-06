"""module irafglobals.py -- widely used IRAF constants and objects

yes, no         Boolean values
IrafError       Standard IRAF exception
Verbose         Flag indicating verbosity level
pyrafDir        Directory with these Pyraf programs
userIrafHome    User's IRAF home directory (./ or ~/iraf/)
userWorkingHome User's working home directory (the directory
                when this module gets imported.)
EOF             End-of-file indicator object
INDEF           Undefined object
IrafTask        "Tag" class for IrafTask type.
IrafPkg         "Tag" class for IrafPkg type

This is defined so it is safe to say 'from irafglobals import *'

The tag classes do nothing except allow checks of types via (e.g.)
isinstance(o,IrafTask).  Including it here decouples the other classes
from the module that actually implements IrafTask, greatly reducing the
need for mutual imports of modules by one another.

$Id: irafglobals.py,v 1.1 2003/10/08 18:33:12 dencheva Exp $

R. White, 2000 January 5
"""

import os, sys, types
_os = os
_sys = sys
_types = types
del os, sys, types

class IrafError(Exception):
    pass

# -----------------------------------------------------
# Verbose: verbosity flag
# -----------------------------------------------------

# make Verbose an instance of a class so it can be imported
# into other modules and changed by them

class _VerboseClass:
    """Container class for verbosity (or other) value"""
    def __init__(self, value=0): self.value = value
    def set(self, value): self.value = value
    def get(self): return self.value
    def __cmp__(self, other): return cmp(self.value, other)
    def __nonzero__(self): return (self.value != 0)
    def __str__(self): return str(self.value)

Verbose = _VerboseClass()

# -----------------------------------------------------
# userWorkingHome is current working directory
# -----------------------------------------------------

userWorkingHome = _os.getcwd()

# -----------------------------------------------------
# pyrafDir is directory containing this script
# -----------------------------------------------------

if __name__ == "__main__":
    thisfile = _sys.argv[0]
else:
    thisfile = __file__
# follow links to get to the real filename
while _os.path.islink(thisfile):
    thisfile = _os.readlink(thisfile)
pyrafDir = _os.path.dirname(thisfile)
del thisfile

if not pyrafDir: pyrafDir = userWorkingHome
# change relative directory paths to absolute and normalize path
pyrafDir = _os.path.normpath(_os.path.join(userWorkingHome, pyrafDir))

# -----------------------------------------------------
# userIrafHome is location of user's IRAF home directory
# -----------------------------------------------------

# If login.cl exists here, use this directory as home.
# Otherwise look for ~/iraf.

if _os.path.exists('./login.cl'):
    userIrafHome = _os.path.join(userWorkingHome,'')
else:
    userIrafHome = _os.path.join(_os.environ['HOME'],'iraf','')
    if not _os.path.exists(userIrafHome):
        # no ~/iraf, just use '.' as home
        userIrafHome = _os.path.join(userWorkingHome,'')

# -----------------------------------------------------
# Boolean constant class
# -----------------------------------------------------

class _Boolean:
    """Class of boolean constant object"""
    def __init__(self, value):
        # change value to 1 or 0
        if value:
            self.__value = 1
        else:
            self.__value = 0
        self.__strvalue = ["no", "yes"][self.__value]

    def __copy__(self):
        """Don't bother to make a copy"""
        return self

    def __deepcopy__(self, memo=None):
        """Don't bother to make a copy"""
        return self

    def __cmp__(self, other):
        if isinstance(other, self.__class__):
            return cmp(self.__value, other.__value)
        elif type(other) is _types.StringType:
            # If a string, compare with string value of this parameter
            # Allow uppercase "YES", "NO" as well as lowercase
            # Also allows single letter abbrevation "y" or "n"
            ovalue = other.lower()
            if len(ovalue) == 1:
                return cmp(self.__strvalue[0], ovalue)
            else:
                return cmp(self.__strvalue, ovalue)
        elif type(other) in (_types.IntType, _types.FloatType):
            # If a number, compare with this value
            return cmp(self.__value, other)
        else:
            return 1

    def __nonzero__(self): return self.__value
    def __repr__(self): return self.__strvalue
    def __str__(self): return self.__strvalue
    def __int__(self): return self.__value
    def __float__(self): return float(self.__value)

# create yes, no boolean values

yes = _Boolean(1)
no = _Boolean(0)


# -----------------------------------------------------
# define end-of-file object
# if printed, says 'EOF'
# if converted to integer, has value -2 (special IRAF value)
# Implemented as a singleton, although the singleton
# nature is not really essential
# -----------------------------------------------------

class _EOFClass:
    """Class of singleton EOF (end-of-file) object"""
    def __init__(self):
        global EOF
        if EOF is not None:
            # only allow one to be created
            raise RuntimeError("Use EOF object, not _EOFClass")

    def __copy__(self):
        """Not allowed to make a copy"""
        return self

    def __deepcopy__(self, memo=None):
        """Not allowed to make a copy"""
        return self

    def __cmp__(self, other):
        if isinstance(other, self.__class__):
            # Despite trying to create only one EOF object, there
            # could be more than one.  All EOFs are equal.
            return 0
        elif type(other) is _types.StringType:
            # If a string, compare with 'EOF'
            return cmp("EOF", other)
        elif type(other) in (_types.IntType, _types.FloatType):
            # If a number, compare with -2
            return cmp(-2, other)
        else:
            return 1

    def __repr__(self): return "EOF"
    def __str__(self): return "EOF"
    def __int__(self): return -2
    def __float__(self): return -2.0

# initialize EOF to None first so singleton scheme works

EOF = None
EOF = _EOFClass()

# -----------------------------------------------------
# define IRAF-like INDEF object
# -----------------------------------------------------

class _INDEFClass:
    """Class of singleton INDEF (undefined) object"""
    def __init__(self):
        global INDEF
        if INDEF is not None:
            # only allow one to be created
            raise RuntimeError("Use INDEF object, not _INDEFClass")

    def __copy__(self):
        """Not allowed to make a copy"""
        return self

    def __deepcopy__(self, memo=None):
        """Not allowed to make a copy"""
        return self

    def __cmp__(self, other):
        if isinstance(other, self.__class__):
            # Despite trying to create only one INDEF object, there
            # could be more than one.  All INDEFs are equal.
            return 0
        else:
            #XXX Note this implies INDEF is equivalent to +infinity
            #XXX This is the only way to get the right answer
            #XXX on tests of equality to INDEF
            #XXX Replace this once rich comparisons (__gt__, __lt__, etc.)
            #XXX are available (Python 1.6?)
            return 1

    def __repr__(self): return "INDEF"
    def __str__(self): return "INDEF"

    __oct__ = __str__
    __hex__ = __str__

    def __nonzero__(self): return 0

    # all operations on INDEF return INDEF

    def __add__(self, other): return self

    __sub__    = __add__
    __mul__    = __add__
    __rmul__   = __add__
    __div__    = __add__
    __mod__    = __add__
    __divmod__ = __add__
    __pow__    = __add__
    __lshift__ = __add__
    __rshift__ = __add__
    __and__    = __add__
    __xor__    = __add__
    __or__     = __add__

    __radd__    = __add__
    __rsub__    = __add__
    __rmul__    = __add__
    __rrmul__   = __add__
    __rdiv__    = __add__
    __rmod__    = __add__
    __rdivmod__ = __add__
    __rpow__    = __add__
    __rlshift__ = __add__
    __rrshift__ = __add__
    __rand__    = __add__
    __rxor__    = __add__
    __ror__     = __add__

    def __neg__(self): return self

    __pos__    = __neg__
    __abs__    = __neg__
    __invert__ = __neg__

    # it is a bit nasty having these functions not return
    # the promised int, float, etc. -- but it is required that
    # this object act just like an undefined value for one of
    # those types, so I need to pretend it really is a legal
    # int or float

    __int__    = __neg__
    __long__   = __neg__
    __float__  = __neg__


# initialize INDEF to None first so singleton scheme works

INDEF = None
INDEF = _INDEFClass()

# -----------------------------------------------------
# tag classes
# -----------------------------------------------------

class IrafTask:
    pass

class IrafPkg(IrafTask):
    pass
