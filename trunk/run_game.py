#! /usr/bin/env python

import sys
import os
try:
    libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib'))
    sys.path.insert(0, libdir)
except:
    # probably running inside py2exe which doesn't set __file__
    pass


import game
import gext_test

if __name__ == '__main__':
#    game.main()
    gext_test.main()

