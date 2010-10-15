import code
import StringIO
from raptus.torii.interpreter import AbstractInterpreter

class InteractiveConsole(code.InteractiveConsole):
    pass


class Python(AbstractInterpreter):
    """ default interpreter for torii
    """

    def __init__(self, locals):
        self.console = InteractiveConsole(locals)

    def getPrompt1(self):
        return '>>> '

    def getPrompt2(self):
        return '... '

    def getReadline(self):
        return None

    def resetStream(self):
        """ reset stdout and stderr stream. Called each time before
            a command is executed.
        """

    def push(self, line):
        return self.console.push(line)
    
    def runcode(self,code):
        self.console.runcode(code)

    
    def complete(self, text):
        return []
    
    def getStdout(self):
        return StringIO.StringIO()
    
    def getErrorStream(self):
        return StringIO.StringIO()
    
    def getSyntaxErrorStream(self):
        return StringIO.StringIO()
    
