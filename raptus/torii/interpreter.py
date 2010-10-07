

class AbstractInterpreter(object):
    
    def __init__(self, locals):
        pass

    def getPrompt1(self):
        """ return prompt like >>>
        """

    def getPrompt2(self):
        """ return prompt like ...
        """

    def getReadline(self):
        """ return readline instance for the client 
        """

    def resetStream(self):
        """ reset stdout and stderr stream. Called each time before
            a command is executed.
        """

    def push(self, line):
        """ push a single code line
        """
    
    def runcode(self,code):
        """ run a code-object
        """
    
    def complete(self, text):
        """ code completion
        """
    
    def getStdout(self):
        """ get the stdout for this cycle
        """
    
    def getErrorStream(self):
        """ return all generated errors in this cycle
        """
    def getSyntaxErrorStream(self):
        """ return all generated syntax-errors in this cycle
        """
    