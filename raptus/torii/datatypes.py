import sys
import StringIO
from threading import Thread
from ZServer.datatypes import ServerFactory
from ZServer import CONNECTION_LIMIT, requestCloseOnExec
import socket, os, threading
import asyncore
import Zope2
from code import InteractiveInterpreter,InteractiveConsole
from codeop import CommandCompiler, compile_command
import traceback
from raptus.torii import config
from raptus.torii.socketExtended import SocketExtended


class ToriiServer(asyncore.dispatcher):
    def __init__(self, path, logger):
        asyncore.dispatcher.__init__(self)
        try:
            os.unlink(path)
        except os.error:
            pass
        self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.bind(path)
        self.listen(256)
        self.log_info('ToriiServer is running\n\tSocketpath: %s' % path)
        self.locals = dict()
        
    def handle_accept(self):
        Thread(target=self.handle_communication).start()
        
    def handle_communication(self):
        try:
            conn, addr = self.accept()
        except socket.error:
            self.log_info('Server accept() threw an exception', 'warning')
            return
        
        old_stdout = sys.stdout
        try:
            db, aname, version_support = Zope2.bobo_application._stuff
            connection = db.open()
            #interpreter = InteractiveInterpreter(dict(app=Zope2.bobo_application(connection)))
            #std = eval(response,dict(__builtins__=None),dict(app=Zope2.bobo_application(db)))
            
            #InteractiveConsole(dict(app=Zope2.bobo_application(connection))).interact()
            app=Zope2.bobo_application(connection)
            self.locals.update(dict(app=app))
            conn.send(config.PS1)
            commands = []
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                commands.append(data)
                sys.stdout = StringIO.StringIO()
                try:
                    code = compile_command('\n'.join(commands))
                except:
                    self.showtraceback()
                    code = False
                if code is not None:
                    if code:
                        try:
                            exec code in self.locals
                        except:
                            self.showtraceback()
                    conn.send(sys.stdout.getvalue())
                    sys.stdout = old_stdout
                    conn.send(config.PS1)
                    commands= []
                else:
                    conn.send(config.PS2)
            
            connection.close()
            del sys.stdout
            conn.shutdown(1)
        finally:
            sys.stdout = old_stdout

            
    def readable(self):
        return len(asyncore.socket_map) < CONNECTION_LIMIT

    def writable (self):
        return True
    
    def listen(self, num):
        # override asyncore limits for nt's listen queue size
        self.accepting = 1
        return self.socket.listen(num)

    def create_socket(self, family, type):
        #asyncore.dispatcher.create_socket(self, family, type)
        self.family_and_type = family, type
        #self.socket = socket.socket(family, type)
        self.socket = SocketExtended(family, type)
        self._fileno = self.socket.fileno()
        self.add_channel()
        requestCloseOnExec(self.socket)


    def showtraceback(self):
        try:
            type, value, tb = sys.exc_info()
            sys.last_type = type
            sys.last_value = value
            sys.last_traceback = tb
            tblist = traceback.extract_tb(tb)
            del tblist[:1]
            list = traceback.format_list(tblist)
            if list:
                list.insert(0, "Traceback (most recent call last):\n")
            list[len(list):] = traceback.format_exception_only(type, value)
        finally:
            tblist = tb = None
        map(sys.stdout.write, list)

class ToriiFactory(ServerFactory):
    
    def __init__(self, section):
        self.section = section
        
    def prepare(self, defaulthost='', dnsresolver=None, module=None, env=None, portbase=None):
        pass
        
    def create(self):
        from ZServer.AccessLogger import access_logger
        return ToriiServer(self.section.address.address, access_logger)


