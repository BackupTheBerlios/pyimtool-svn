#
#  PyRAF_AquaAppDelegate.py
#  PyRAF-Aqua
#
#  Created by Francesco Pierfederici on 8/14/04.
#  Copyright (c) 2004 __MyCompanyName__. All rights reserved.
#

from utilities import *

from AsyncInteractiveConsole import *
from PseudoUTF8Input import *
from PseudoUTF8Output import *


try:
    sys.ps1
except AttributeError:
    sys.ps1 = ">>> "
try:
    sys.ps2
except AttributeError:
    sys.ps2 = "... "

DEBUG_DELEGATE = 0
PASSTHROUGH = (
   'deleteBackward:',
   'complete:',
   'moveRight:',
   'moveLeft:',
)

NibClassBuilder.extractClasses("MainMenu")
class AppDelegate (NibClassBuilder.AutoBaseClass):
    """
    AppDelegate is a delegate/controller for a NSTextView,
    turning it into a full featured interactive Python interpreter.
    """

    #
    #  Outlets - for documentation only
    #

    _NIBOutlets_ = (
        (NSTextView,    'textView',         'The interpreter'),
    )

    #
    #  NSApplicationDelegate methods
    #

    def applicationDidFinishLaunching_(self, aNotification):
        self.textView.setFont_(self.font())
        self.textView.setContinuousSpellCheckingEnabled_(False)
        self.textView.setRichText_(False)
        self._executeWithRedirectedIO(self._interp)

    #
    #  NIB loading protocol
    #

    def awakeFromNib(self):
        self = super(AppDelegate, self).init()
        self._font = NSFont.userFixedPitchFontOfSize_(10)
        self._stderrColor = NSColor.redColor()
        self._stdoutColor = NSColor.blueColor()
        self._codeColor = NSColor.blackColor()
        self._historyLength = 50
        self._history = [u'']
        self._historyView = 0
        self._characterIndexForInput = 0
        self._stdin = PseudoUTF8Input(self._nestedRunLoopReaderUntilEOLchars_)
        #self._stdin = PseudoUTF8Input(self.readStdin)
        self._stderr = PseudoUTF8Output(self.writeStderr_)
        self._stdout = PseudoUTF8Output(self.writeStdout_)
        self._isInteracting = False
        self._console = AsyncInteractiveConsole()
        self._interp = self._console.asyncinteract(
            write=self.writeCode_,
        ).next
        self._autoscroll = True

    #
    #  Modal input dialog support
    #

    def _nestedRunLoopReaderUntilEOLchars_(self, eolchars):
        """
        This makes the baby jesus cry.

        I want co-routines.
        """
        app = NSApplication.sharedApplication()
        window = self.textView.window()
        self.setCharacterIndexForInput_(self.lengthOfTextView())
        # change the color.. eh
        self.textView.setTypingAttributes_({
            NSFontAttributeName:self.font(),
            NSForegroundColorAttributeName:self.codeColor(),
        })
        while True:
            event = app.nextEventMatchingMask_untilDate_inMode_dequeue_(
                NSAnyEventMask,
                NSDate.distantFuture(),
                NSDefaultRunLoopMode,
                True)
            if (event.type() == NSKeyDown) and (event.window() == window):
                eol = event.characters()
                if eol in eolchars:
                    break
            app.sendEvent_(event)
        cl = self.currentLine()
        if eol == '\r':
            self.writeCode_('\n')
        return cl+eol

    #
    #  Interpreter functions
    #

    def _executeWithRedirectedIO(self, fn, *args, **kwargs):
        old = sys.stdin, sys.stdout, sys.stderr
        if self._stdin is not None:
            sys.stdin = self._stdin
        sys.stdout, sys.stderr = self._stdout, self._stderr
        try:
            rval = fn(*args, **kwargs)
        finally:
            sys.stdin, sys.stdout, sys.stderr = old
            self.setCharacterIndexForInput_(self.lengthOfTextView())
        return rval

    def executeLine_(self, line):
        self.addHistoryLine_(line)
        self._executeWithRedirectedIO(self._executeLine_, line)
        self._history = filter(None, self._history)
        self._history.append(u'')
        self._historyView = len(self._history) - 1

    def _executeLine_(self, line):
        self._interp()(line)
        self._more = self._interp()

    def executeInteractiveLine_(self, line):
        self.setIsInteracting(True)
        try:
            self.executeLine_(line)
        finally:
            self.setIsInteracting(False)

    def replaceLineWithCode_(self, s):
        idx = self.characterIndexForInput()
        ts = self.textView.textStorage()
        ts.replaceCharactersInRange_withAttributedString_(
            (idx, len(ts.mutableString())-idx), self.codeString_(s))

    #
    #  History functions
    #

    def historyLength(self):
        return self._historyLength

    def setHistoryLength_(self, length):
        self._historyLength = length

    def addHistoryLine_(self, line):
        line = line.rstrip('\n')
        if self._history[-1] == line:
            return False
        if not line:
            return False
        self._history.append(line)
        if len(self._history) > self.historyLength():
            self._history.pop(0)
        return True

    def historyDown_(self, sender):
        if self._historyView == (len(self._history) - 1):
            return
        self._history[self._historyView] = self.currentLine()
        self._historyView += 1
        self.replaceLineWithCode_(self._history[self._historyView])
        self.moveToEndOfLine_(self)

    def historyUp_(self, sender):
        if self._historyView == 0:
            return
        self._history[self._historyView] = self.currentLine()
        self._historyView -= 1
        self.replaceLineWithCode_(self._history[self._historyView])
        self.moveToEndOfLine_(self)

    #
    #  Convenience methods to create/write decorated text
    #

    def _formatString_forOutput_(self, s, name):
        return NSAttributedString.alloc().initWithString_attributes_(
            s,
            {
                NSFontAttributeName:self.font(),
                NSForegroundColorAttributeName:getattr(self, name+'Color')(),
            },
        )

    def _writeString_forOutput_(self, s, name):
        self.textView.textStorage().appendAttributedString_(getattr(self, name+'String_')(s))

        window = self.textView.window()
        app = NSApplication.sharedApplication()
        st = time.time()
        now = time.time

        if self._autoscroll:
            self.textView.scrollRangeToVisible_((self.lengthOfTextView(), 0))

        while app.isRunning() and now() - st < 0.01:
            event = app.nextEventMatchingMask_untilDate_inMode_dequeue_(
                NSAnyEventMask,
                NSDate.dateWithTimeIntervalSinceNow_(0.01),
                NSDefaultRunLoopMode,
                True)

            if event is None:
                continue

            if (event.type() == NSKeyDown) and (event.window() == window):
                chr = event.charactersIgnoringModifiers()
                if chr == 'c' and (event.modifierFlags() & NSControlKeyMask):
                    raise KeyboardInterrupt

            app.sendEvent_(event)


    codeString_   = lambda self, s: self._formatString_forOutput_(s, 'code')
    stderrString_ = lambda self, s: self._formatString_forOutput_(s, 'stderr')
    stdoutString_ = lambda self, s: self._formatString_forOutput_(s, 'stdout')
    writeCode_    = lambda self, s: self._writeString_forOutput_(s, 'code')
    writeStderr_  = lambda self, s: self._writeString_forOutput_(s, 'stderr')
    writeStdout_  = lambda self, s: self._writeString_forOutput_(s, 'stdout')

    #
    #  Accessors
    #

    def more(self):
        return self._more

    def font(self):
        return self._font

    def setFont_(self, font):
        self._font = font

    def stderrColor(self):
        return self._stderrColor

    def setStderrColor_(self, color):
        self._stderrColor = color

    def stdoutColor(self):
        return self._stdoutColor

    def setStdoutColor_(self, color):
        self._stdoutColor = color

    def codeColor(self):
        return self._codeColor

    def setStdoutColor_(self, color):
        self._codeColor = color

    def isInteracting(self):
        return self._isInteracting

    def setIsInteracting(self, v):
        self._isInteracting = v

    def isAutoScroll(self):
        return self._autoScroll

    def setAutoScroll(self, v):
        self._autoScroll = v


    #
    #  Convenience methods for manipulating the NSTextView
    #

    def currentLine(self):
        return self.textView.textStorage().mutableString()[self.characterIndexForInput():]

    def moveAndScrollToIndex_(self, idx):
        self.textView.scrollRangeToVisible_((idx, 0))
        self.textView.setSelectedRange_((idx, 0))

    def characterIndexForInput(self):
        return self._characterIndexForInput

    def lengthOfTextView(self):
        return len(self.textView.textStorage().mutableString())

    def setCharacterIndexForInput_(self, idx):
        self._characterIndexForInput = idx
        self.moveAndScrollToIndex_(idx)

    #
    #  NSTextViewDelegate methods
    #

    def textView_completions_forPartialWordRange_indexOfSelectedItem_(self, aTextView, completions, (begin, length), index):
        txt = self.textView.textStorage().mutableString()
        end = begin+length
        while (begin>0) and (txt[begin].isalnum() or txt[begin] in '._'):
            begin -= 1
        while not txt[begin].isalnum():
            begin += 1
        return self._console.recommendCompletionsFor(txt[begin:end])

    def textView_shouldChangeTextInRange_replacementString_(self, aTextView, aRange, newString):
        begin, length = aRange
        lastLocation = self.characterIndexForInput()
        if begin < lastLocation:
            # no editing anywhere but the interactive line
            return NO
        newString = newString.replace('\r', '\n')
        if '\n' in newString:
            if begin != lastLocation:
                # no pasting multiline unless you're at the end
                # of the interactive line
                return NO
            # multiline paste support
            #self.clearLine()
            newString = self.currentLine() + newString
            for s in newString.strip().split('\n'):
                self.writeCode_(s+'\n')
                self.executeLine_(s)
            return NO
        return YES

    def textView_willChangeSelectionFromCharacterRange_toCharacterRange_(self, aTextView, fromRange, toRange):
        return toRange
        begin, length = toRange
        if length == 0 and begin < self.characterIndexForInput():
            # no cursor movement off the interactive line
            return fromRange
        return toRange

    def textView_doCommandBySelector_(self, aTextView, aSelector):
        # deleteForward: is ctrl-d
        if self.isInteracting():
            if aSelector == 'insertNewline:':
                self.writeCode_('\n')
            return NO
        responder = getattr(self, aSelector.replace(':','_'), None)
        if responder is not None:
            responder(aTextView)
            return YES
        else:
            if DEBUG_DELEGATE and aSelector not in PASSTHROUGH:
                print aSelector
            return NO

    #
    #  doCommandBySelector "posers" on the textView
    #

    def insertTabIgnoringFieldEditor_(self, sender):
        # this isn't terribly necessary, b/c F5 and opt-esc do completion
        # but why not
        sender.complete_(self)

    def moveToBeginningOfLine_(self, sender):
        self.moveAndScrollToIndex_(self.characterIndexForInput())

    def moveToEndOfLine_(self, sender):
        self.moveAndScrollToIndex_(self.lengthOfTextView())

    def moveToBeginningOfLineAndModifySelection_(self, sender):
        begin, length = self.textView.selectedRange()
        pos = self.characterIndexForInput()
        if begin+length > pos:
            self.textView.setSelectedRange_((pos, begin+length-pos))
        else:
            self.moveToBeginningOfLine_(sender)

    def moveToEndOfLineAndModifySelection_(self, sender):
        begin, length = self.textView.selectedRange()
        pos = max(self.characterIndexForInput(), begin)
        self.textView.setSelectedRange_((pos, self.lengthOfTextView()))

    def insertNewline_(self, sender):
        line = self.currentLine()
        self.writeCode_('\n')
        self.executeInteractiveLine_(line)

    moveToBeginningOfParagraph_ = moveToBeginningOfLine_
    moveToEndOfParagraph_ = moveToEndOfLine_
    insertNewlineIgnoringFieldEditor_ = insertNewline_
    moveDown_ = historyDown_
    moveUp_ = historyUp_



