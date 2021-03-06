"""clcache.py: Implement cache for Python translations of CL tasks

$Id: clcache.py,v 1.1 2003/10/08 18:33:12 dencheva Exp $

R. White, 2000 January 19
"""

import os, sys, types, string
import filecache
from irafglobals import Verbose, userIrafHome, pyrafDir

# set up pickle so it can pickle code objects

import copy_reg, marshal, types
try:
    import cPickle
    pickle = cPickle
except ImportError:
    import pickle

def code_unpickler(data):
    return marshal.loads(data)

def code_pickler(code):
    return code_unpickler, (marshal.dumps(code),)

copy_reg.pickle(types.CodeType, code_pickler, code_unpickler)

# Code cache is implemented using a dictionary clFileDict and
# a list of persistent dictionaries (shelves) in cacheList.
#
# - clFileDict uses CL filename as the key and has
#   the md5 digest of the file contents as its value.
#   The md5 digest is automatically updated if the file changes.
#
# - the persistent cache has the md5 digest as the key
#       and the Pycode object as the value.
#
# This scheme allows files with different path names to
# be found in the cache (since the file contents, not the
# name, determine the shelve key) while staying up-to-date
# with changes of the CL file contents when the script is
# being developed.

import dirshelve, stat, md5

_versionKey = 'CACHE_VERSION'
_currentVersion = "v1"

class _FileContentsCache(filecache.FileCacheDict):
    def __init__(self):
        # create file dictionary with md5 digest as value
        filecache.FileCacheDict.__init__(self,filecache.MD5Cache)

class _CodeCache:

    """Python code cache class

    Note that old out-of-date cached code never gets
    removed in this system.  That's because another CL
    script might still exist with the same code.  Need a
    utility to clean up the cache by looking for unused keys...
    """

    def __init__(self, cacheFileList):
        cacheList = []
        flist = []
        nwrite = 0
        for file in cacheFileList:
            db = self._cacheOpen(file)
            if db is not None:
                cacheList.append(db)
                nwrite = nwrite+db[0]
                flist.append(file)
        self.clFileDict = _FileContentsCache()
        self.cacheList = cacheList
        self.cacheFileList = flist
        self.nwrite = nwrite
        # flag indicating preference for system cache
        self.useSystem = 0
        if not cacheList:
            self.warning("Unable to open any CL script cache, "
                    "performance will be slow")
        elif nwrite == 0:
            self.warning("Unable to open any CL script cache for writing")

    def _cacheOpen(self, filename):
        """Open shelve database in filename and check version

        Returns tuple (writeflag, shelve-object) on success or None on failure.
        """
        # first try opening the cache read-write
        try:
            fh = dirshelve.open(filename)
            writeflag = 1
        except dirshelve.error:
            # initial open failed -- try opening the cache read-only
            try:
                fh = dirshelve.open(filename,"r")
                writeflag = 0
            except dirshelve.error:
                self.warning("Unable to open CL script cache file %s" %
                        (filename,))
                return None
        # check version of cache -- don't use it if out-of-date
        if fh.has_key(_versionKey):
            oldVersion = fh[_versionKey]
        elif len(fh) == 0:
            fh[_versionKey] = _currentVersion
            oldVersion = _currentVersion
        else:
            oldVersion = 'v0'
        if oldVersion == _currentVersion:
            return (writeflag, fh)
        # open succeeded, but version looks out-of-date
        fh.close()
        rv = None
        msg = ["CL script cache file is obsolete version (old %s, current %s)" %
                (`oldVersion`, `_currentVersion`)]
        if not writeflag:
            # we can't replace it if we couldn't open it read-write
            msg.append("Ignoring obsolete cache file %s" % filename)
        else:
            # try renaming the old file and creating a new one
            rfilename = filename + "." + oldVersion
            try:
                os.rename(filename, rfilename)
                msg.append("Renamed old cache to %s" % rfilename)
                try:
                    # create new cache file
                    fh = dirshelve.open(filename)
                    fh[_versionKey] = _currentVersion
                    msg.append("Created new cache file %s" % filename)
                    rv = (writeflag, fh)
                except dirshelve.error:
                    msg.append("Could not create new cache file %s" % filename)
            except OSError:
                msg.append("Could not rename old cache file %s" % filename)
        self.warning(string.join(msg,"\n"))
        return rv

    def warning(self, msg, level=0):

        """Print warning message to stderr, using verbose flag"""

        if Verbose >= level:
            sys.stdout.flush()
            sys.stderr.write(msg + "\n")
            sys.stderr.flush()

    def writeSystem(self, value=1):

        """Add scripts to system cache instead of user cache"""

        if value==0:
            self.useSystem = 0
        elif self.cacheList:
            writeflag, cache = self.cacheList[-1]
            if writeflag:
                self.useSystem = 1
            else:
                self.warning("System CL script cache is not writable")
        else:
            self.warning("No CL script cache is active")

    def close(self):

        """Close all cache files"""

        for writeflag, cache in self.cacheList:
            cache.close()
        self.cacheList = []
        self.nwrite = 0
        # Note that this does not delete clFileDict since the
        # in-memory info for files already read is still OK
        # (Just in case there is some reason to close cache files
        # while keeping _CodeCache object around for future use.)

    def __del__(self):
        self.close()

    def getIndex(self, filename, source=None):

        """Get cache key for a file or filehandle"""

        if filename:
            return self.clFileDict.get(filename)
        elif source:
            # there is no filename, but return md5 digest of source as key
            return md5.new(source).digest()

    def add(self, index, pycode):

        """Add pycode to cache with key = index.  Ignores if index=None."""

        if index is None or self.nwrite==0: return
        if self.useSystem:
            # system cache is last in list
            cacheList = self.cacheList[:]
            cacheList.reverse()
        else:
            cacheList = self.cacheList
        for writeflag, cache in cacheList:
            if writeflag:
                cache[index] = pycode
                return

    def get(self, filename, mode="proc", source=None):

        """Get pycode from cache for this file.

        Returns tuple (index, pycode).  Pycode=None if not found
        in cache.  If mode != "proc", assumes that the code should not be
        cached.
        """

        if mode != "proc": return None, None

        index = self.getIndex(filename, source=source)
        if index is None: return None, None

        for i in range(len(self.cacheList)):
            writeflag, cache = self.cacheList[i]
            if cache.has_key(index):
                pycode = cache[index]
                #XXX
                # kluge for backward compatibility -- force type of object
                # eliminate this eventually
                if not hasattr(pycode, 'setFilename'):
                    import cl2py
                    pycode.__class__ = cl2py.Pycode
                    if hasattr(pycode, 'filename'):
                        del pycode.filename
                    # replace outmoded object in the cache
                    if writeflag:
                        cache[index] = pycode
                #XXX
                pycode.index = index
                pycode.setFilename(filename)
                return index, pycode
        return index, None

    def remove(self, filename):

        """Remove pycode from cache for this file or IrafTask object.

        This deletes the entry from the shelve persistent database, under
        the assumption that this routine may be called to fix a bug in
        the code generation (so we don't want to keep the old version of
        the Python code around.)
        """

        if type(filename) is not types.StringType:
            try:
                task = filename
                filename = task.getFullpath()
            except (AttributeError, TypeError):
                raise TypeError(
                        "Filename parameter must be a string or IrafCLTask")
        index = self.getIndex(filename)
        # system cache is last in list
        irange = range(len(self.cacheList))
        if self.useSystem: irange.reverse()
        nremoved = 0
        for i in irange:
            writeflag, cache = self.cacheList[i]
            if cache.has_key(index):
                if writeflag:
                    del cache[index]
                    self.warning("Removed %s from CL script cache %s" % \
                            (filename,self.cacheFileList[i]), 2)
                    nremoved = nremoved+1
                else:
                    self.warning("Cannot remove %s from read-only "
                            "CL script cache %s" % \
                            (filename,self.cacheFileList[i]))
        if nremoved==0:
            self.warning("Did not find %s in CL script cache" % filename, 2)


# create code cache

userCacheDir = os.path.join(userIrafHome,'pyraf')
if not os.path.exists(userCacheDir):
    try:
        os.mkdir(userCacheDir)
        print 'Created directory %s for cache' % userCacheDir
    except OSError:
        print 'Could not create directory %s' % userCacheDir

dbfile = 'clcache'
codeCache = _CodeCache([
        os.path.join(userCacheDir,dbfile),
        os.path.join(pyrafDir,dbfile),
        ])
del userCacheDir, dbfile
