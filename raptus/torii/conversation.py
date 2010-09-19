import sys, os
import socket
import StringIO
import cPickle
import threading
import Zope2
import Globals
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
        

class Conversation(threading.Thread):
    
    def __init__(self, connection):
        super(Conversation, self).__init__()
        self.connection = connection
        self.locals = config.utilities
        
        self.interpreter = make_IPython(argv=[],embedded=True,user_global_ns=self.locals)
        self.interpreter.set_hook('result_display',result_display)
        color = self.interpreter.rc.colors
        self.interpreter.InteractiveTB = AutoFormattedTB(mode = 'Plain',
                                                         color_scheme=color,
                                                         tb_offset = 1)
        self.interpreter.SyntaxTB = SyntaxTB(color_scheme=color)
        self.arguments = self.conversation(carrier.FetchArguments()).arguments
        self.locals.update(arguments=self.arguments)
        
    def run(self):
        dbConnection = Zope2.DB.open()
        application=Zope2.bobo_application(connection=dbConnection)
        self.locals.update(dict(app=application))

        for name, func in config.properties.items():
            if hasattr(func, 'func_code'):
                di = func.func_globals
                di.update(self.locals)
                res = eval(func.func_code,di)
                self.locals.update({name:res})
                continue
            try:
                res = func()
                self.locals.update({name:res})
                continue
            except:
                self.locals.update({name:func})

        mode = dict(    help = lambda: self.conversation(carrier.PrintHelpText()),
                        debug = self.interactiveMode,
                        list = self.listScripts,
                        run = self.runScript,
                   )
        if not Globals.DevelopmentMode:
            msg  = """
                       Sorry, but run the debug mode on productive Zope is too risky!
                       Pleas stop your Server and run it in the Foreground (fg) mode.
                   """
            mode.update(dict(debug=lambda: self.conversation(carrier.PrintText(msg))))
        
        
        try:
            if len(self.arguments) > 1 and self.arguments[1] in mode:
                mode[self.arguments[1]]()
            else:
                mode['help']()
            self.conversation(carrier.ExitTorii())
                
        except:
            dbConnection.close()
            self.connection.close()
    
    def listScripts(self):
        self.conversation(carrier.PrintText('here is a list with all available scripts:\n'))
        for name, path in config.scripts.items():
            self.conversation(carrier.PrintText(' '*10+name))

    def runScript(self):
        name = self.arguments[2]
        path = config.scripts.get(name)
        f = file(path)
        code = compile_command(f.read(),path,'exec')
        f.close()
        self.interpreter.runcode(code)
        
    def interactiveMode(self):
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

    