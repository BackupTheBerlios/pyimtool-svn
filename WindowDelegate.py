from my_defs import *


NibClassBuilder.extractClasses("MainMenu")

# class defined in MainMenu.nib
class WindowDelegate (NibClassBuilder.AutoBaseClass):
    # the actual base class is NSObject
    # The following outlets are added to the class:
    # <none>
    
    def windowShouldClose_ (self, sender):
        NSApp ().terminate_ (self)
        return (YES)
