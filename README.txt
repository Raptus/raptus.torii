Introduction
============
Torii allow the access to a running zope server over a unix-domain-socket. Torii make
also possible to run scripts from the command line to the server. In addition it's provide a python-
prompt connected to the zope-server. It means the full access of the Zope and ZODB at the runtime.


Usage
=====
If you use the buildout-recipe, a shell-script are generated in buildout-directory/bin/torii.
After starting the zope server, open a new shell, go to your project and type ./bin/torii

Options:
--------

help            this help
                  
debug           interactiv mode
                 
list            summary-list of all available scripts

run <script>    run the given script


Installation
============

The simplest way to install torii is to use raptus.recipe.torii with a buildout for your
project. This will add the required information in the zope.conf and build a startup
script. The recipe provides two buildout-variables. The first is named ${torii:additonal-conf}
with it hold the additional information for the zope.conf. This way you're self responsible
how the zope.conf are created. The second variable ${torii:eggs} is a list with all required
eggs to add in the python-path.

Options
-------
socket-path
    where the unix-domain-socket are located 
threaded
    If True torii created each connection a new thread therefore other ports aren't stopped.
    Default is False
extends
    additional-packages for extending torii. e.g. raptus.troii.plone
params
    additional-parameters required for the extending packages.
    notation: key:value;key:value or key:value'newline'key:value

Example
-------
::

    [buildout]
    parts =
        torii
        ...(other parts)...

    [torii]
    recipe = raptus.recipe.torii
    socket-path = ${buildout:directory}/var/torii.sock
    threaded = True
    extends =
        raptus.torii.plone
        raptus.torii.ipython
    params =
        plone-location:test.plone

    [instance]
    recipe = plone.recipe.zope2instance
    zope-conf-additional = ${torii:additional-conf}
    eggs =
    ...(other eggs)...
    ${buildout:eggs}
    ${torii:eggs}
    ...

    or

    [instance]
    recipe = plone.recipe.zope2instance
    zope-conf-additional = 
    <zodb_db myproject>
      mount-point /myproject
      <filestorage>
        path ${buildout:directory}/var/filestorage/myproject-prod.fs
        blob-dir ${buildout:directory}/var/blobstorage/prod
      </filestorage>
    </zodb_db>
    ${torii:additional-conf}
    eggs =
    ...(other eggs)...
    ${buildout:eggs}
    ${torii:eggs}
    ...


Additional components
=====================

raptus.torii.plone
    This additional package make the interface to plone. It provides some scripts, a global 
    variable 'plone' and set the siteManager(access to persistence zope.components ) at the startup

raptus.torii.ipython
    A implementation of ipython. Code-completion, readline and colored python prompt.


Create new additional components
================================

Torii is pluggable. If you write a package use following attributes explained below. These
attributes are stored in your module (__init__.py) and by each connection they were read by torii.

utilities = dict(name=method)
    utilities are a set of helper functions. They will appear as globals
    in your python prompt. The globals can be extended with additional
    packages. To extend take a look in raptus.torii.plone.

properties = dict(name=method)
    properties are a set of helper attributes. Similar to the utilities, but
    properties are called by each connection. The call of the function performed
    in the context of the connection. This means you can use local attributes
    in your function, like app, arguments ... Only the return value is stored 
    in the globals. To extend take a look in raptus.torii.plone.


scripts = dict(name=path)
    scripts can be run directly without the python prompt over torii. It's
    easy to customize you own scripts. Again please take a look
    at raptus.torii.plone


interpreter = Python
    The standard python interpreter. To create you own interpreter subclass
    interpreter.AbstractInterpreter and override all methods. Take a look at
    raptus.torii.python and raptus.torii.ipython.ipython


Examples
========

Change the front-page text on the plonesite::

    # ./bin/torii debug
    Available global variables:
    conversation
    ls
    app
    sdir
    plone
    arguments
    
    In [1]: frontpage = plone['front-page']
    
    In [2]: frontpage.setText('The power of torii')
    
    In [3]: import transaction
    
    In [4]: transaction.commit()

Get all plone users::
    
    In [5]: plone.acl_users.getUsers()
    Out[5]: [<PloneUser 'dagobert_duck'>, <PloneUser 'donald_duck'>]


Tests
=====
Sorry, but no automated test are existing sadly. This project was created on SnowLeopard and
was running on plone 3 and plone 4.


Copyright and credits
=====================

raptus.torii is copyright 2010 by raptus_ , and is licensed under the GPL. 
See LICENSE.txt for details.

.. _raptus: http://www.raptus.ch/ 