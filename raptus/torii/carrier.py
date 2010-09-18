import sys
from optparse import OptionParser
from raptus.torii import config
import cPickle
import readline


class Completer(object):
    
    def __init__(self, sock):
        self.sock = sock
        self.memo = {'':[config.tab_replacement]}
        
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
    """ The communicatin between ZopeServer and Client goes over the instance BaseCarrier.
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
    """ CounterCarrier is a request from the client to the server.
    """
    def executable(self, interpreter):
        print 'override this methode in counterCarrier'
    
    
    
class FetchArguments(BaseCarrier):
    
    def executable(self, client):
        self.arguments = sys.argv

class SendDisplayHook(BaseCarrier):
    def __init__(self, displayhook):
        self.displayhook = displayhook
    
    def executable(self, client):
        sys.readline = self.displayhook

class GetCodeLine(BaseCarrier):
    
    def __init__(self,interpreter):
        self.readline = interpreter.readline
        self.ps1 = str(sys.displayhook.prompt1)
        self.ps2 = str(sys.displayhook.prompt2)

    def setReadline(self, client):
        readline = self.readline
        readline.parse_and_bind('tab: complete')
        readline.set_completer(Completer(client.sock).completer)
    
    def executable(self, client):
        self.setReadline(client)
        sys.ps1 = self.ps1
        sys.ps2 = self.ps2
        self.line = raw_input(sys.ps1)
        

class GetNextCodeLine(GetCodeLine):
    
    def executable(self, client):
        self.setReadline(client)
        self.line = raw_input(sys.ps2)


class SendStdout(BaseCarrier):
    
    
    def __init__(self, stringIO):
        self.stringIO = stringIO
        self.promt_out = str(sys.displayhook.prompt_out)
    
    def executable(self, client):
        self.stringIO.seek(0)
        sys.stdout.write(self.promt_out)
        for out in self.stringIO:
            print >> sys.stdout, out


class SendStderr(SendStdout):
    
    def executable(self, client):
        self.stringIO.seek(0)
        for out in self.stringIO:
            print >> sys.stderr, out

class PrintHelpText(BaseCarrier):
    
    def executable(self, client):
        print >> sys.stdout, client.__doc__

class PrintText(BaseCarrier):
    
    def __init__(self, text):
        self.text = text
    
    def executable(self, client):
        print >> sys.stdout, self.text

class ExitTorii(BaseCarrier):
    
    def executable(self, client):
        client.sock.close()
        sys.exit()

class FetchCompleter(BaseCounterCarrier):
    def __init__(self, text, state):
        self.text = text
        self.state = state
    def executable(self, interpreter):
        self.result = interpreter.complete(self.text)
