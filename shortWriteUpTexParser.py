#
# Copyright (c) 2015 by Antonio Molina García-Retamero. All Rights Reserved.
#

from pylatexenc import latex2text
import re

class ShortWriteUpParser(object):
    """Class for parsing Short Writeups from non standard latex"""
    def __init__(self, tex):
        super(ShortWriteUpParser, self).__init__()
        #self.tex = tex.split('\n')

    def _parsing(self):
        section = []
        for l in text:
            if l[0] == '\\':
                if l[1:] == 'Version':
                    self.version =

    def _accentParsing(arg):
        pass

# r'.*\\Keywords{(.*?)}'
