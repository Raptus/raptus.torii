import socket
import time

class SocketExtended(socket.socket):
    
    def recv(self):
        while True:
            try:
                return super(Socket, self).recv()
                break
            except socket.error:
                time.sleep(0.01)
                pass
        
    def send(self, *args, **kw):
        time.sleep(0.01)
        super(Socket, self).send(*args, **kw)
