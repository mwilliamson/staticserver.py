#!/usr/bin/env python

import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='staticserver',
    version='0.1.0',
    description='Serve up static content over HTTP',
    long_description=read("README"),
    author='Michael Williamson',
    url='http://github.com/mwilliamson/staticserver.py',
    packages=['staticserver'],
    install_requires=['pyramid==1.4b3'],
)

