import sys
import socket
import cPickle
import StringIO
from optparse import OptionParser
from raptus.torii import config

class Client(object):
    
    __doc__ = """
     A torii is a traditional Japanese gate most commonly 
     found at the entrance of or within a Shinto shrine.
     But in the zopy-world raptus.torii provide a gate to a
     running zope-server (holy-zopy). The access to the server can be
     get of differnt ways. here the manual:

                  
     help        this help
                  
     <script> -h help of giving script
                  
     <script>    run the giving script
                 
     list        sammary-list of all avaiable scripts
                 in_* internal
                 ex_* external (managed by a paht defined by you self)
                 ce_* created scripts
                  
     debug       interavtiv mode

     create      start as debug mode but record all the giving input
                 and store them in the directory of externals-script
              """
              
    
    def __init__(self, path):
        self.path = path
        
    
    def main(self):
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.path)
            ioSocket = sock.makefile()
            while True:
                carrier = cPickle.load(ioSocket)
                carrier.executable(self)
                if carrier.sendBack:
                    cPickle.dump(carrier, sock.makefile())
        except socket.error, msg:
                    print msg
        except KeyboardInterrupt:
            sock.close()
        sock.close()


