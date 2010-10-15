import sys,os
import utilities
from raptus.torii.python import Python

utilities = dict(sdir=utilities.sdir, ls=utilities.ls)
""" utilities are a set of helper function. this will appear as globals
    in your python prompt. This globals can be extended with additionals
    packages. To extend take a look in raptus.torii.plone. Before the prompt
    is started we add all locals to this function. This way is possible to
    use app, conversation,.. and others attributes.
"""
properties = dict()
""" properties are a set of helper attributes. Similar to the utilities, but
    properties are called each connection. The call of the function performed
    in the context of the connection. This means you can use local attributes
    in your function, like app, arguments ... Only the return value are stored 
    in the globals. To extend take a look in raptus.torii.plone.
"""

scripts = dict(pack= '%s/scripts/pack.py' % os.path.dirname(__file__))
""" scripts can be run directly without the a python prompt over torii. It's
    easy to customize you own scripts. Again pleas take a look
    at raptus.torii.plone
"""

interpreter = Python
""" the standard interpreter
"""

tab_replacement = '    '

