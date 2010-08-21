import sys
from optparse import OptionParser
from raptus.torii import config

def completer( text, state):
    if not state:
        return 'teeeeeeest'




class BaseCarrier(object):
    __doc__="""
        The communicatin between ZopeServer and Client goes over the instance BaseCarrier.
        The server send a pickle-instance to the client. The clinet recive the object and run
        a executable methode on this class. After all this the client send the object back
        to the ZopeServer.
    """
    
    def executable(self, client):
        """ this methode is called from the clinet
            each time while recived this object.
        """
        print "ooops you need to override this methode in the BaseCarrier"
        
    
class FetchOptions(BaseCarrier):
    
    def executable(self, client):
        self.parser = OptionParser()

class SendDisplayHook(BaseCarrier):
    def __init__(self, displayhook):
        self.displayhook = displayhook
    
    def executable(self, client):
        sys.readline = self.displayhook

class GetCodeLine(BaseCarrier):
    
    def __init__(self,interpreter):
        self.readline = interpreter.readline
        self.ps1 = sys.displayhook.ps1_str
        self.ps2 = sys.displayhook.ps1_str
    
    def setReadline(self):
        import readline
        
        readline = self.readline
        readline.parse_and_bind('tab: complete')
        readline.set_completer(completer)
    
    def executable(self, client):
        import sys
        self.setReadline()
        sys.ps1 = self.ps1
        sys.ps2 = self.ps2
        self.line = raw_input(sys.ps1)
        del self.counterquestion
        
    def counterquestion(self, interpreter):
        interpreter.Completer.complete(text, state)

class GetNextCodeLine(GetCodeLine):
    
    def executable(self, client):
        self.setReadline()
        self.line = raw_input(sys.ps2)


class SendStdout(BaseCarrier):
    
    
    def __init__(self, stringIO):
        self.stringIO = stringIO
    
    def executable(self, client):
        self.stringIO.seek(0)
        for out in self.stringIO:
            sys.stdout.write(out)
        sys.stdout.write('\n')


class SendStderr(SendStdout):
    
    def executable(self, client):
        self.stringIO.seek(0)
        for out in self.stringIO:
            sys.stderr.write(out)
        sys.stdout.write('\n')

