
from utilities import *

class AsyncInteractiveConsole(InteractiveConsole):
    lock = False
    buffer = None

    def __init__(self, *args, **kwargs):
        InteractiveConsole.__init__(self, *args, **kwargs)
        self.locals['__interpreter__'] = self

    def asyncinteract(self, write=None, banner=None):
        if self.lock:
            raise ValueError, "Can't nest"
        self.lock = True
        if write is None:
            write = self.write
        cprt = u'Type "help", "copyright", "credits" or "license" for more information.'
        if banner is None:
            write(u"Python %s in %s\n%s\n" % (
                sys.version,
                NSBundle.mainBundle().objectForInfoDictionaryKey_('CFBundleName'),
                cprt,
            ))
        else:
            write(banner + '\n')
        more = 0
        _buff = []
        try:
            while True:
                if more:
                    prompt = sys.ps2
                else:
                    prompt = sys.ps1
                write(prompt)
                # yield the kind of prompt we have
                yield more
                # next input function
                yield _buff.append
                more = self.push(_buff.pop())
        except:
            self.lock = False
            raise
        self.lock = False

    def resetbuffer(self):
        self.lastbuffer = self.buffer
        InteractiveConsole.resetbuffer(self)

    def runcode(self, code):
        try:
            exec code in self.locals
        except SystemExit:
            raise
        except:
            self.showtraceback()
        else:
            if softspace(sys.stdout, 0):
                print


    def recommendCompletionsFor(self, word):
        parts = word.split('.')
        if len(parts) > 1:
            # has a . so it must be a module or class or something
            # using eval, which shouldn't normally have side effects
            # unless there's descriptors/metaclasses doing some nasty
            # get magic
            objname = '.'.join(parts[:-1])
            try:
                obj = eval(objname, self.locals)
            except:
                return None, 0
            wordlower = parts[-1].lower()
            if wordlower == '':
                # they just punched in a dot, so list all attributes
                # that don't look private or special
                prefix = '.'.join(parts[-2:])
                check = [
                    (prefix+_method)
                    for _method
                    in dir(obj)
                    if _method[:1] != '_' and _method.lower().startswith(wordlower)
                ]
            else:
                # they started typing the method name
                check = filter(lambda s:s.lower().startswith(wordlower), dir(obj))
        else:
            # no dots, must be in the normal namespaces.. no eval necessary
            check = sets.Set(dir(__builtins__))
            check.update(keyword.kwlist)
            check.update(self.locals)
            wordlower = parts[-1].lower()
            check = filter(lambda s:s.lower().startswith(wordlower), check)
        check.sort()
        return check, 0
