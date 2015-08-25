#
# Copyright (c) 2015 by Antonio Molina Garcia-Retamero. All Rights Reserved.
#

import sys
import logging
import os

from PyQt4 import QtCore, QtGui
from os import listdir
from DataPreservationGUI import Ui_MainWindow
from WriteUps import WriteUp, ShortWriteUp, LongWriteUp
from DataManager import DataManager
from LogingTextArea import LoggingTextArea

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

def _processShortWriteUp():
    pass

def _processLongWriteUp():
    pass

class MainGUI(QtGui.QMainWindow):
    def __init__(self, parent=None):
        logger.info("Loading GUI...")
        QtGui.QWidget.__init__(self,parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Custom logging area
        self.loggingTextEdit = LoggingTextArea(self.ui.frame)
        self.loggingTextEdit.setGeometry(QtCore.QRect(10, 10, 541, 560))
        self.loggingTextEdit.setObjectName(_fromUtf8("loggingTextEdit"))
        self.loggingTextEdit.setReadOnly(True)
        # Handling logs into app
        sh = logging.StreamHandler(self.loggingTextEdit)
        sh.setFormatter(logging.Formatter('%(message)s'))
        sh.setLevel(logging.INFO)
        logger.addHandler(sh)
        logger.setLevel(logging.DEBUG)

        # Some corrections
        self.ui.tabWidget.setTabText(0, "Short write up")
        self.ui.tabWidget.setTabText(1, "Long write up")
        self.ui.tabWidget_2.setTabText(0, "Single file")
        self.ui.tabWidget_2.setTabText(1, "Multiple files")
        self.ui.inyectCheckBox.setEnabled(False)

        # Event binding
        self.ui.pushButton.clicked.connect(self._selectLongFile)
        self.ui.searchSingleShortButton.clicked.connect(self._selectSingleShortFile)
        self.ui.parseSingleShortButton.clicked.connect(self._parseSingleShortFile)
        self.ui.searchMultipleShortButton.clicked.connect(self._selectMultipleShortFiles)
        self.ui.parseMultipleShortButton.clicked.connect(self._parseMultipleShortFiles)
        self.ui.loadDirectoryMultipleShortButton.clicked.connect(self._loadDirectoryMultipleShort)
        self.ui.processButton.clicked.connect(self._processWriteUp)
        self.ui.tabWidget.currentChanged.connect(self._tabChanged)
        self.ui.tabWidget_2.currentChanged.connect(self._tabChanged_2)

        # Other stuff
        self.bp = None

        # Data Preservation stuff
        self._writeup = None
        self._writeups = []
        self._filenames = []

        # Stuff for testing
        logger.info("Welcome to the data preservation software for TeX processing.")

    def _initLongWriteUp():
        self.lwu = LongWriteUp()

    def _tabChanged(self, index):
        logger.debug("Selected tab: " + str(index))
        if index == 0:
            self.ui.inyectCheckBox.setEnabled(False)
        else:
            self.ui.inyectCheckBox.setEnabled(True)

    def _tabChanged_2(self, index):
        logger.debug("Selected tab_2" + str(index))

    def _selectLongFile(self):
        filename = QtGui.QFileDialog.getOpenFileName()
        logger.info("Selected: " + filename)
        self.ui.fileEdit.setText(filename)

    def _selectSingleShortFile(self):
        #TODO: I have to filter only .tex files
        filename = QtGui.QFileDialog.getOpenFileName()
        logger.info("Parsing file: " + filename)
        try:
            writeup = ShortWriteUp.parseFromTex(filename)
            self.setWriteUp(writeup)
            logger.info(writeup)
            logger.info("Parsing done...")
            self.ui.texShortTb.setText(filename)
        except Exception as ex:
            logger.info("Error in parsing the document. Please, select a file with the correct latex structure")
            logger.debug(str(ex))
            #TODO the error chain for getting a message to the user

    def _parseSingleShortFile(self):
        '''Deprecated: it is done on the selection step'''
        filename = self.ui.texShortTb.toPlainText()
        logger.info("Parsing file " + filename.split('/')[-1] + " from TeX")
        try:
            writeup = ShortWriteUp.parseFromTex(filename)
            self.setWriteUp(writeup)
            logger.info("Parsing done...")
        except Exception as ex:
            logger.info("Error in parsing the document. Please, select a file with the correct latex structure")
            logger.debug(str(ex))
            #TODO the error chain for getting a message to the user

    def _selectMultipleShortFiles(self):
        self._filenames = QtGui.QFileDialog.getOpenFileNames()
        self.ui.loadededFilesShortTextEdit.clear()
        for filename in self._filenames:
            self.ui.loadededFilesShortTextEdit.insertPlainText(filename.split('/')[-1]+"\n")
        self._writeups = []

    def _loadDirectoryMultipleShort(self):
        directory = QtGui.QFileDialog.getExistingDirectory()
        logger.debug(directory)
        self._filenames = [directory+"/"+f for f in listdir(directory)]
        self.ui.loadededFilesShortTextEdit.clear()
        if len(self._filenames) < 1:
            logger.info("Please, select files before parsing")
            return
        failed = 0
        succeed = 0
        for filename in self._filenames:
            logger.info("Parsing file " + filename.split('/')[-1] + " from TeX")
            try:
                self._writeups.append(ShortWriteUp.parseFromTex(filename))
                self.ui.loadededFilesShortTextEdit.insertPlainText(filename.split('/')[-1]+"\n")
                succeed += 1
                logger.info(self._writeups[-1])
                logger.info("Parsing done...")
            except Exception as ex:
                failed += 1
                logger.debug(str(ex))
                logger.info("Error in parsing the document. Please, select a file with the correct latex structure")
                #TODO the error chain for getting a message to the user
        logger.info("For " + str(len(self._filenames)) + " documents:\nFailed: " + str(failed) + "\nSucceed: " + str(succeed))

    def _parseMultipleShortFiles(self):
        '''Deprecated: it is done on the selection step'''
        failed = 0
        succeed = 0
        if len(self._filenames) < 1:
            logger.info("Please, select files before parsing")
            return
        for filename in self._filenames:
            logger.info("Parsing file " + filename.split('/')[-1] + " from TeX")
            try:
                self._writeups.append(ShortWriteUp.parseFromTex(filename))
                succeed += 1
                logger.info(self._writeups[-1])
                logger.info("Parsing done...")
            except Exception as ex:
                failed += 1
                logger.debug(str(ex))
                logger.info("Error in parsing the document. Please, select a file with the correct latex structure")
                #TODO the error chain for getting a message to the user
        logger.info("For " + str(len(self._filenames)) + " documents:\nFailed: " + str(failed) + "\nSucceed: " + str(succeed))

    def _processWriteUp(self):
        pdf = self.ui.PDFCheckBox.isChecked()
        html = self.ui.HTMLCheckBox.isChecked()
        if self.ui.tabWidget.currentIndex() == 0: # Short WriteUp
            if self.ui.tabWidget_2.currentIndex() == 0: # Single File
                if self._writeup is None:
                    logger.info("No write up ready for processing")
                else:
                    self._writeup.process(pdf, html)
                    if self.ui.persistCheckBox.isChecked:
                        DataManager.saveShortWriteUp(self._writeup)
            else: # Multiple File
                logger.info("Start processing " + str(len(self._writeups)) + " writeups")
                #TODO: Compare what to do. If multiple workers or just one
                # Working in background
                self.bp = BackgroundProcessor(self._writeups, pdf, html)
                self.connect(self.bp, QtCore.SIGNAL("backLogMessage(QString)"), self._backProccessorMessage)
                self.bp.start()
                logger.info("Multiple files processing done")
        else: # Long WriteUp
            pass

    def setWriteUp(self, writeUp):
        if isinstance(writeUp, WriteUp):
            logger.debug("Si, es un WriteUp")
            self._writeup = writeUp
            # Updating the UI
            self.ui.nameShorttb.setText(writeUp.name)
            self.ui.idShortTb.setText(writeUp.ID)
            self.ui.authorShortTb.setText(writeUp.authorName)
            self.ui.keywordsShortTb.setText(writeUp.keywords)
        else:
            # TODO this the right way
            logger.debug("No es un writeUp")

    def _backProccessorMessage(self, msg):
        logger.info(msg)

class BackgroundProcessor(QtCore.QThread):
    def __init__(self, writeups, pdf, html):
        QtCore.QThread.__init__(self)
        self._writeups = writeups
        self._pdf = pdf
        self._html = html

    def run(self):
        for writeup in self._writeups:
            self._logMessage("Processing: " + writeup.filename)
            # TODO: This manual processing shouldn't be done
            self._logMessage("Copying file for processing")
            os.system('cp {0} {1}'.format(writeup.filename, "aux/" + writeup.filename.split('/')[-1]))
            # print(swu.getHyperSetup())
            if self._pdf:
                self._logMessage("Creating PDF/A")
                writeup._generatePDF()
            # Get reduced html
            if self._html:
                self._logMessage("Creating reduced HTML")
                writeup._generateHtml()
            # Cleaning files
            self._logMessage("Cleaning auxiliar files")
            os.system('rm {0}.*'.format(writeup.filename.split('/')[-1].split('.')[0])) # TODO: It can be improved
            os.system('rm *.png')


    def _logMessage(self, msg):
        self.emit(QtCore.SIGNAL('backLogMessage(QString)'), msg)



logger = logging.getLogger("DataPreservationLogger")

if __name__ == '__main__':
    # App creation
    app = QtGui.QApplication(sys.argv)
    myapp = MainGUI()
    # Global logging setup
    fh = logging.FileHandler('dpGUI.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Running
    myapp.show()
    sys.exit(app.exec_())
