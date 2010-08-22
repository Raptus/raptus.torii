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
from IPython.Prompts import CachedOutput
from codeop import compile_command
from pprint import PrettyPrinter
import traceback
from raptus.torii import config,utility
from raptus.torii import carrier


def result_display(self, arg):
    from IPython.hooks import result_display
    result_display(self, arg)
    import StringIO
    self.outStringIO = StringIO.StringIO()
    if self.rc.pprint:
        out =  PrettyPrinter().pformat(arg)
        if '\n' in out:
            self.outStringIO.write('\n')
        print >> self.outStringIO, out
    else:
        print >> self.outStringIO, repr(arg)
    return None 

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
        """
        cache = CachedOutput(interpreter,
                             interpreter.rc.cache_size,
                             interpreter.rc.pprint,
                             input_sep = interpreter.rc.separate_in,
                             output_sep = interpreter.rc.separate_out,
                             output_sep2 = interpreter.rc.separate_out2,
                             ps1 = interpreter.rc.prompt_in1,
                             ps2 = interpreter.rc.prompt_in2,
                             ps_out = interpreter.rc.prompt_out,)
        """
        try:
            db, aname, version_support = Zope2.bobo_application._stuff
            connection = db.open()

            app=Zope2.bobo_application(connection)
            self.locals.update(dict(app=app))
            options = self.conversation(conn, carrier.FetchOptions())
            self.locals.update(parser=options.parser)
            #self.conversiontion(conn, carrier.SendDisplayHook(interpreter.readline))
            while True:
                input = self.conversation(conn, carrier.GetCodeLine(self.interpreter))
                try:
                    while self.interpreter.push(input.line):
                        input = self.conversation(conn, carrier.GetNextCodeLine(self.interpreter))
                except Exception, mesg:
                    self.conversation(conn, carrier.SendStderr(genutils.Term.cout.stream))
                self.conversation(conn, carrier.SendStdout(self.interpreter.outStringIO))
                
            connection.close()
            del sys.stdout
            conn.shutdown(1)
            
        except Exception,meg:
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


