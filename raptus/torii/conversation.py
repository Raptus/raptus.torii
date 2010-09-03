import sys, os
import socket
import StringIO
import cPickle
from threading import Thread
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
        

class Conversation(object):
    
    def __init__(self, conn):
        self.connection = conn
        self.locals = dict(sdir=utility.sdir, ls=utility.ls)
        
        self.interpreter = make_IPython(argv=[],embedded=True,user_global_ns=self.locals)
        self.interpreter.set_hook('result_display',result_display)
        color = self.interpreter.rc.colors
        self.interpreter.InteractiveTB = AutoFormattedTB(mode = 'Plain',
                                                         color_scheme=color,
                                                         tb_offset = 1)
        self.interpreter.SyntaxTB = SyntaxTB(color_scheme=color)

    
    def run(self):
        self.interactiveMode()
        
    def interactiveMode(self):

        try:
            db, aname, version_support = Zope2.bobo_application._stuff
            dbConnection = db.open()
            app=Zope2.bobo_application(dbConnection)
            self.locals.update(dict(app=app))
            options = self.conversation( carrier.FetchOptions())
            self.locals.update(parser=options.parser)

            while True:
                """ reset stdout and stderr stream each time
                """
                self.interpreter.outStringIO = StringIO.StringIO()
                self.interpreter.InteractiveTB.errStringIO = StringIO.StringIO()
                self.interpreter.SyntaxTB.errStringIO = StringIO.StringIO()
                
                input = self.conversation(carrier.GetCodeLine(self.interpreter))
                try:
                    while self.interpreter.push(input.line):
                        input = self.conversation(carrier.GetNextCodeLine(self.interpreter))
                except Exception, mesg:
                    pass
                stderr = self.interpreter.InteractiveTB.errStringIO
                if stderr.len:
                    self.conversation(carrier.SendStderr(stderr))
                stderr = self.interpreter.SyntaxTB.errStringIO
                if stderr.len:
                    self.conversation(carrier.SendStderr(stderr))
                stdout = self.interpreter.outStringIO
                if stdout.len:
                    self.conversation(carrier.SendStdout(stdout))
                
            
        except Exception,meg:
            dbConnection.close()
            self.connection.close()

    def conversation(self, carrierObject):
        cPickle.dump(carrierObject, self.connection.makefile())
        while True:
            obj = cPickle.load(self.connection.makefile())
            if isinstance(obj, carrier.BaseCarrier):
                break;
            else:
                obj.executable(self.interpreter)
                cPickle.dump(obj, self.connection.makefile())
        return obj
    
    