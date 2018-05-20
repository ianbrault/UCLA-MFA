"""
env.py
loads environment variables from a .env file

author: Ian Brault <ianbrault@ucla.edu>
created: 19 May 2018
"""

import os

def load():
    """
    loads environment variables from a .env file
    @raise FileNotFoundError if no such .env file is present
    """

    envpath = os.path.dirname(os.path.realpath(__file__)) + "/.env"
    envfile = open(envpath, 'r')

    for envvar in envfile.readlines():
        key, val = envvar.split('=')
        if val[-1] == '\n': val = val[:-1]
        os.environ[key] = val
