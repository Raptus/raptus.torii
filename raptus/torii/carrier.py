import sys
from optparse import OptionParser
from raptus.torii import config
import cPickle

class Completer(object):
    
    def __init__(self, sock):
        self.sock = sock
        self.memo = {'':[]}
        
    def completer(self, text, state):
        if not self.memo.has_key(text):
            cPickle.dump(FetchCompleter(text,state), self.sock.makefile())
            carrier = cPickle.load(self.sock.makefile())
            self.memo.update({text:carrier.result})
        for cmd in self.memo[text]:
            if cmd.startswith(text):
                if not state:
                    return cmd
                else:
                    state -= 1



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
        
class BaseCounterCarrier(object):
    __doc__ = """
        CounterCarrier is a request from the client to the server.
    """
    def executable(self, interpreter):
        print 'override this methode in counterCarrier'
    
    
    
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
    
    def setReadline(self, client):
        import readline
        readline = self.readline
        readline.parse_and_bind('tab: complete')
        readline.set_completer(Completer(client.sock).completer)
    
    def executable(self, client):
        import sys
        self.setReadline(client)
        sys.ps1 = self.ps1
        sys.ps2 = self.ps2
        self.line = raw_input(sys.ps1)
        

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


class FetchCompleter(BaseCounterCarrier):
    def __init__(self, text, state):
        self.text = text
        self.state = state
    def executable(self, interpreter):
        self.result = interpreter.complete(self.text)
