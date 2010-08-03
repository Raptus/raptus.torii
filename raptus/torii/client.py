import socket
import sys
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
        self.mode = sys.argv.pop()
        
    
    def main(self):
        
        if self.mode == 'help':
            print self.__doc__
        elif self.mode == 'debug':
            self.connect()


    def connect(self):
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.path)
            response =''
            while True:
                while True:
                    try:
                        data = sock.recv(4096)
                        break
                    except socket.error:
                        pass
                if not data:
                    break
                if data.find(config.PS1) == 0 or data.find(config.PS2) == 0:
                    sock.send(self.input(data))
                else:
                    sys.stdout.write(data)
            sock.close()
        except socket.error, msg:
                    print msg

    def input(self, data):
        if self.mode == 'debug':
            input = raw_input(data)
            return '%s%s' % (input, input == '' and '\n' or '' )
        
        
        
        
        