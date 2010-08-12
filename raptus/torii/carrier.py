import sys
from optparse import OptionParser
from raptus.torii import config

class BaseCarrier(object):
    __doc__="""
        The communicatin between ZopeServer and Client goes over the instance BaseCarrier.
        The server send a pickle-instance to the client. The clinet recive the object and run
        a executable methode on this class. After all this the client send the object back
        to the ZopeServer.
    """
    
    sendBack = True
    
    def executable(self, client):
        """ this methode is called from the clinet
            each time while recived this object.
        """
        print "ooops you need to override this methode in the BaseCarrier"
        
    
class FetchOptions(BaseCarrier):
    
    def executable(self, client):
        self.parser = OptionParser()


class GetCodeLine(BaseCarrier):
    
    def executable(self, client):
        self.line = raw_input(config.PS1)


class GetNextCodeLine(BaseCarrier):
    
    def executable(self, client):
        self.line = raw_input(config.PS2)


class SendStdout(BaseCarrier):
    
    sendBack = False
    
    def __init__(self, stringIO):
        self.stringIO = stringIO
    
    def executable(self, client):
        self.stringIO.seek(0)
        for out in self.stringIO:
            sys.stdout.write(out)


class SendStderr(SendStdout):
    
    def executable(self, client):
        self.stringIO.seek(0)
        for out in self.stringIO:
            sys.stderr.write(out)

