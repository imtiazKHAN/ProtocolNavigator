#
# setup.py for building the Protocol Navigator application for Mac.
#
# How to build:
#
#   $ pythonw32 setup.py py2app
#   $ mv 'dist/Protocol Navigator.app' 'dist/pn.app'
#   $ ditto --rsrc --arch i386 'dist/pn.app' 'dist/Protocol Navigator.app'
#   $ rm -rf 'dist/pn.app'
#

from setuptools import setup, Extension
import sys
import os
import os.path
import numpy
# fix from
#  http://mail.python.org/pipermail/pythonmac-sig/2008-June/020111.html
import pytz
pytz.zoneinfo = pytz.tzinfo
pytz.zoneinfo.UTC = pytz.UTC
import pilfix

import util.version
f = open("util/frozen_version.py", "w")
f.write("# MACHINE_GENERATED\nversion_string = '%s'" % util.version.version_string)
f.close()

APPNAME = 'Protocol Navigator'
APP = ['protocolnavigator.py']
OPTIONS = {'argv_emulation': True,
           'iconfile' : "icons/cpa.icns",
           'includes' : [],
           'packages' : ['./icons'],
           'excludes' : ['Cython', 'pylab', 'Tkinter', 'cellprofiler'],
           'resources' : [],
          }

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    name = APPNAME,
)

