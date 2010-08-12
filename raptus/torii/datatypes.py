import sys, os
import socket
import StringIO
import cPickle
from threading import Thread
from ZServer.datatypes import ServerFactory
from ZServer import CONNECTION_LIMIT, requestCloseOnExec
import asyncore
import Zope2
from codeop import compile_command
import traceback
from raptus.torii import config,utility
from raptus.torii import carrier

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
        self.locals = dict(sdir=utility.sdir, ls=utility.ls)
        
    def handle_accept(self):
        #todo in next step
        self.debugmode()
        #Thread(target=self.debugmode).start()
        
    def debugmode(self):
        try:
            conn, addr = self.accept()
        except socket.error:
            self.log_info('Server accept() threw an exception', 'warning')
            return
        
        old_stdout = sys.stdout
        try:
            db, aname, version_support = Zope2.bobo_application._stuff
            connection = db.open()

            app=Zope2.bobo_application(connection)
            self.locals.update(dict(app=app))
            
            cPickle.dump(carrier.FetchOptions(), conn.makefile())
            options = cPickle.load(conn.makefile())
            self.locals.update(parser=options.parser)
            
            cPickle.dump(carrier.GetCodeLine(),conn.makefile())

            commands = []
            while True:
                commands.append(cPickle.load(conn.makefile()).line)
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
                            cPickle.dump(carrier.SendStderr(self.showtraceback()),conn.makefile())
                    cPickle.dump(carrier.SendStdout(sys.stdout),conn.makefile())
                    sys.stdout = old_stdout
                    cPickle.dump(carrier.GetCodeLine(),conn.makefile())
                    commands= []
                else:
                    cPickle.dump(carrier.GetNextCodeLine(),conn.makefile())
            
            connection.close()
            del sys.stdout
            conn.shutdown(1)
            
        except Exception,meg:
            conn.close()

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
        asyncore.dispatcher.create_socket(self, family, type)
        self.family_and_type = family, type
        self.socket = socket.socket(family, type)
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
            err = StringIO.StringIO()
            err.writelines(list)
            return err

class ToriiFactory(ServerFactory):
    
    def __init__(self, section):
        self.section = section
        
    def prepare(self, defaulthost='', dnsresolver=None, module=None, env=None, portbase=None):
        pass
        
    def create(self):
        from ZServer.AccessLogger import access_logger
        return ToriiServer(self.section.path.address, access_logger)


