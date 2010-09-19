import sys
import utilities

utilities = dict(sdir=utilities.sdir, ls=utilities.ls)
""" utilities are a set of helper function. this will appear as globals
    in your python prompt. This globals can be extended with additionals
    packages. To extend take a look in raptus.torii.plone.
"""
properties = dict()
""" properties are a set of helper attributes. Similar to the utilities, but
    properties are called each connection. The call of the function performed
    in the context of the connection. This means you can use local attributes
    in your function, like app, arguments ... Only the return value are stored 
    in the globals. To extend take a look in raptus.torii.plone.
"""

scripts = dict()
""" scripts can be run directly without the a python prompt over torii. It's
    easy to customize you own scripts. Again pleas take a look
    at raptus.torii.plone
"""

tab_replacement = '    '

