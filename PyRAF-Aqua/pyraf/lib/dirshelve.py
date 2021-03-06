"""Version of shelve that uses files in a directory with binary pickle format

Allows simultaneous read-write access to the data since
the OS allows multiple processes to have access to the
file system.

$Id: dirshelve.py,v 1.1 2003/10/08 18:33:12 dencheva Exp $

XXX keys, len may be incorrect if directory database is modified
XXX by another process after open

R. White, 2000 Sept 26
"""

import dirdbm, shelve

# tuple of errors that can be raised
error = (dirdbm.error, )

class Shelf(shelve.Shelf):
    """Extension of Shelf using binary pickling"""

    def __getitem__(self, key):
        f = shelve.StringIO(self.dict[key])
        try:
            return shelve.Unpickler(f).load()
        except EOFError:
            # apparently file is truncated; delete it and raise
            # and exception
            del self.dict[key]
            raise KeyError("Corrupted or truncated file for key %s "
                    "(bad file has been deleted)" % (`key`,))

    def __setitem__(self, key, value):
        f = shelve.StringIO()
        p = shelve.Pickler(f,1)
        p.dump(value)
        self.dict[key] = f.getvalue()

    def close(self):
        if hasattr(self,'dict') and hasattr(self.dict,'close'):
            try:
                self.dict.close()
            except:
                pass
        self.dict = 0

class DirectoryShelf(Shelf):
    """Shelf implementation using the directory db interface.

    This is initialized with the filename for the dirdbm database.
    """

    def __init__(self, filename, flag='c'):
        Shelf.__init__(self, dirdbm.open(filename, flag))

def open(filename, flag='c'):
    """Open a persistent dictionary for reading and writing.

    Argument is the filename for the dirdbm database.
    """

    return DirectoryShelf(filename, flag)
