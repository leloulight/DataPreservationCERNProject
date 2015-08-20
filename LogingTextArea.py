#
# Copyright (c) 2015 by Antonio Molina Garcia-Retamero. All Rights Reserved.
#


from PyQt4 import QtCore, QtGui

class LoggingTextArea(QtGui.QPlainTextEdit):
    def __init__(self, parent=None):
        super(LoggingTextArea, self).__init__(parent)

    def write(self, string):
        if len(string) > 1:
            self.insertPlainText(string + "\n---------------------------\n")
            self.ensureCursorVisible()

    def flush(self):
        # self.clear()
        pass
