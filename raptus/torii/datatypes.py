import sys, os
import socket
import StringIO
import cPickle
from threading import Thread
from ZServer.datatypes import ServerFactory
from ZServer import CONNECTION_LIMIT, requestCloseOnExec
import asyncore
import Zope2
from IPython.ipmaker import make_IPython
from IPython.ultraTB import AutoFormattedTB as BaseAutoFormattedTB
from IPython.iplib import SyntaxTB as BaseSyntaxTB
from codeop import compile_command
from pprint import PrettyPrinter
import traceback
from raptus.torii import config,utility
from raptus.torii import carrier
from raptus.torii.conversation import Conversation

class ToriiServer(asyncore.dispatcher):
    def __init__(self, path, logger):
        asyncore.dispatcher.__init__(self)
        try:
            os.unlink(path)
        except os.error:
            pass
        self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.bind(path)
        self.listen(1)
        self.socket.setblocking(True)
        self.log_info('ToriiServer is running\n\tSocketpath: %s' % path)
        
    def handle_accept(self):
        #todo in next step
        self.log_info('someone connected on torii server')
        conn, addr = self.accept()
        conversation = Conversation(conn)
        conversation.run()
        #self.log_info('end of torii connection')
        #Thread(target=self.debugmode).start()
        
            
    def readable(self):
        return len(asyncore.socket_map) < CONNECTION_LIMIT

    def writable (self):
        return True
    
    def create_socket(self, family, type):
        asyncore.dispatcher.create_socket(self, family, type)
        #requestCloseOnExec(self.socket)


class ToriiFactory(ServerFactory):
    
    def __init__(self, section):
        self.section = section
        
    def prepare(self, defaulthost='', dnsresolver=None, module=None, env=None, portbase=None):
        pass
        
    def create(self):
        from ZServer.AccessLogger import access_logger
        return ToriiServer(self.section.path.address, access_logger)


