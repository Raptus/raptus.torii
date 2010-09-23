import sys, os
import socket
import csv
from ZServer.datatypes import ServerFactory
from ZServer import CONNECTION_LIMIT, requestCloseOnExec
import asyncore
from raptus.torii import config
from raptus.torii.conversation import Conversation

class ToriiServer(asyncore.dispatcher):
    def __init__(self, path,section, logger):
        asyncore.dispatcher.__init__(self)
        try:
            os.unlink(path)
        except os.error:
            pass
        self.threaded = section.threaded
        self.extends = self.parse_to_list(section.extends)
        self.params = self.parse_to_dict(section.params)
        self.include_ext()
        self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.bind(path)
        self.listen(1)
        self.socket.setblocking(True)
        self.log_info('ToriiServer is running\n\tSocketpath: %s' % path)
        
    def handle_accept(self):
        self.log_info('someone connected on torii server')
        connection, addr = self.accept()
        conversation = Conversation(connection)
        if self.threaded:
            conversation.start()
        else:
            conversation.run()
            
    def readable(self):
        return len(asyncore.socket_map) < CONNECTION_LIMIT

    def writable (self):
        return True
    
    def create_socket(self, family, type):
        asyncore.dispatcher.create_socket(self, family, type)
        
    def parse_to_list(self, string):
        if not string:
            return []
        return [i.strip() for i in string.split(';')]

    def parse_to_dict(self, string):
        res = dict()
        if not string:
            return res
        for i in self.parse_to_list(string):
            k,v = i.split(':')
            res.update({k.strip():v.strip()})
        return res
    
    def include_ext(self):
        for ext in self.extends:
            imp = __import__(ext, None, None, ext)
            
            if hasattr(imp,'initialize'):
                imp.initialize(self.params)
            if hasattr(imp,'utilities'):
                config.utilities.update(imp.utilities)
            if hasattr(imp,'properties'):
                config.properties.update(imp.properties)
            if hasattr(imp,'scripts'):
                config.scripts.update(imp.scripts)
        
    
class ToriiFactory(ServerFactory):
    
    def __init__(self, section):
        self.section = section
        
    def prepare(self, defaulthost='', dnsresolver=None, module=None, env=None, portbase=None):
        pass
        
    def create(self):
        from ZServer.AccessLogger import access_logger
        return ToriiServer(self.section.path.address, self.section, access_logger)


