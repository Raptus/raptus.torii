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

def result_display(self, arg):
    self.outStringIO = StringIO.StringIO()
    if self.rc.pprint:
        out =  PrettyPrinter().pformat(arg)
        if '\n' in out:
            self.outStringIO.write('\n')
        print >> self.outStringIO, out
    else:
        print >> self.outStringIO, repr(arg)
    return None 

class AutoFormattedTB(BaseAutoFormattedTB):
    def __call__(self, *args, **kw):
        self.errStringIO = StringIO.StringIO()
        kw.update(dict(out=self.errStringIO))
        return BaseAutoFormattedTB.__call__(self, *args, **kw)

class SyntaxTB(BaseSyntaxTB):
    def __call__(self, etype, value, elist):
        self.errStringIO = StringIO.StringIO()
        self.last_syntax_error = value
        print >> self.errStringIO, self.text(etype,value,elist)
        

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
        self.locals = dict(sdir=utility.sdir, ls=utility.ls)
        
    def handle_accept(self):
        #todo in next step
        self.log_info('someone connected on torii server')
        self.interactiveMode()
        self.log_info('end of torii connection')
        #Thread(target=self.debugmode).start()
        
    def interactiveMode(self):

        conn, addr = self.accept()
                
        self.interpreter = make_IPython(argv=[],embedded=True,user_global_ns=self.locals)
        self.interpreter.set_hook('result_display',result_display)
        color = self.interpreter.rc.colors
        self.interpreter.InteractiveTB = AutoFormattedTB(mode = 'Plain',
                                                         color_scheme=color,
                                                         tb_offset = 1)
        self.interpreter.SyntaxTB = SyntaxTB(color_scheme=color)

        try:
            db, aname, version_support = Zope2.bobo_application._stuff
            connection = db.open()
            app=Zope2.bobo_application(connection)
            self.locals.update(dict(app=app))
            options = self.conversation(conn, carrier.FetchOptions())
            self.locals.update(parser=options.parser)

            while True:
                """ reset stdout and stderr stream each time
                """
                self.interpreter.outStringIO = StringIO.StringIO()
                self.interpreter.InteractiveTB.errStringIO = StringIO.StringIO()
                self.interpreter.SyntaxTB.errStringIO = StringIO.StringIO()
                
                input = self.conversation(conn, carrier.GetCodeLine(self.interpreter))
                try:
                    while self.interpreter.push(input.line):
                        input = self.conversation(conn, carrier.GetNextCodeLine(self.interpreter))
                except Exception, mesg:
                    pass
                stderr = self.interpreter.InteractiveTB.errStringIO
                if stderr.len:
                    self.conversation(conn, carrier.SendStderr(stderr))
                stderr = self.interpreter.SyntaxTB.errStringIO
                if stderr.len:
                    self.conversation(conn, carrier.SendStderr(stderr))
                stdout = self.interpreter.outStringIO
                if stdout.len:
                    self.conversation(conn, carrier.SendStdout(stdout))
                
            
        except Exception,meg:
            connection.close()
            conn.close()

    def conversation(self, connection, carrierObject):
        cPickle.dump(carrierObject, connection.makefile())
        while True:
            obj = cPickle.load(connection.makefile())
            if isinstance(obj, carrier.BaseCarrier):
                break;
            else:
                obj.executable(self.interpreter)
                cPickle.dump(obj, connection.makefile())

        return obj
            
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


