#
# Copyright (c) 2015 by Antonio Molina Garcia-Retamero. All Rights Reserved.
#

from PyQt4 import QtCore

class ShortDocInyector(QtCore.QThread):
    def __init__(self, htmlFile):
        self.htmlFile = htmlFile

    def run(self):
        # Getting the functions names
        fNames = DataManager.getAllFunctionNames()

        # Getting the HTML
        fHtml = open(htmlFile)
        html = fHtml.read()
        fHtml.close()

        # Looking for function names apparition and replacement
        for fname in fNames:
            if fname in html:
                print("Encontrada: " + fname)
