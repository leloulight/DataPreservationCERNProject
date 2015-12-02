#
# Copyright (c) 2015 by Antonio Molina Garcia-Retamero. All Rights Reserved.
#

import sys
import logging
import os

from PyQt4 import QtCore, QtGui
from os import listdir
from DataPreservationGUI import Ui_MainWindow
from WriteUps import WriteUp, ShortWriteUp, LongWriteUp, DataManager
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
        self.ui.searchLongButton.clicked.connect(self._selectLongFile)
        self.ui.searchSingleShortButton.clicked.connect(self._selectSingleShortFile)
        self.ui.parseSingleShortButton.clicked.connect(self._parseSingleShortFile)
        self.ui.searchMultipleShortButton.clicked.connect(self._selectMultipleShortFiles)
        self.ui.loadDirectoryMultipleShortButton.clicked.connect(self._loadDirectoryMultipleShort)
        self.ui.processButton.clicked.connect(self._processWriteUp)
        self.ui.tabWidget.currentChanged.connect(self._tabChanged)
        self.ui.tabWidget_2.currentChanged.connect(self._tabChanged_2)


        # Other stuff
        self.bp = None
        self._isProcessing = False

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
        filename = QtGui.QFileDialog.getOpenFileName(filter="LaTeX (*.tex)")
        logger.info("Selected: " + filename)
        self.ui.texFileLongTb.setText(filename)
        logger.info("Trying to open the file")
        os.system('open {0}'.format(filename))

    def _selectSingleShortFile(self):
        #TODO: I have to filter only .tex files
        filename = QtGui.QFileDialog.getOpenFileName(filter="LaTeX (*.tex)")
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
        self._filenames = QtGui.QFileDialog.getOpenFileNames(filter="LaTeX (*.tex)")
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
        persist = self.ui.persistCheckBox.isChecked()
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

                self.bp = BackgroundProcessor(self._writeups, pdf, html, persist)
                self.connect(self.bp, QtCore.SIGNAL("backLogMessage(QString)"), self._backProccessorMessage)
                self.connect(self.bp, QtCore.SIGNAL("backProcessFinished()"), self._backProccessorFinished)
                self.bp.start()
                logger.info("Multiple files processing done")
        else: # Long WriteUp
            ID = self.ui.idLongTb.text()
            # if ID == '':
            #     logger.info("Not ID given. All fields required")
            #     return
            title = self.ui.titleLongTb.text()
            # if title == '':
            #     logger.info("Not title given. All fields required")
            #     return
            author = self.ui.authorLongTb.text()
            # if author == '':
            #     logger.info("Not author given. All fields required")
            #     return
            version = self.ui.versionLongTb.text()
            # if version == '':
            #     logger.info("Not version given. All fields required")
            #     return
            copyright = self.ui.copyrightLongTb.text()
            # if copyright == '':
            #     logger.info("Not copyright given. All fields required")
            #     return
            texFile = self.ui.texFileLongTb.toPlainText()
            self._writeup = LongWriteUp(ID, title, version, author, copyright, texFile)
            inyectShortDoc = self.ui.inyectCheckBox.isChecked()
            self._writeup.process(pdf, html, inyectShortDoc)
            if persist:
                DataManager.saveLongWriteUp(self._writeup)

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

    def setIsProcessing(self, isProcessing):
        self._isProcessing = isProcessing
        self.ui.processButton.setEnabled(not isProcessing)

    def _backProccessorMessage(self, msg):
        logger.info(msg)

    def _backProccessorFinished(self):
        self.setIsProcessing(False)

    def closeEvent(self, event):
        print("Cleaning data before exit")
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.system("rm -r -f aux/*")


class BackgroundProcessor(QtCore.QThread):
    def __init__(self, writeups, pdf, html, persist):
        QtCore.QThread.__init__(self)
        self._writeups = writeups
        self._pdf = pdf
        self._html = html
        self._persist = persist

    def run(self):
        auxDir = os.path.dirname(os.path.realpath(__file__)) + "/aux"
        os.chdir(auxDir)
        for writeup in self._writeups:
            self._logMessage("Processing: " + writeup.filename)
            writeup.texFile = writeup.filename.split('/')[-1]
            os.system('cp {0} {1}'.format(writeup.filename, "{0}/{1}".format(auxDir, writeup.texFile)))
            if self._pdf:
                self._logMessage("Creating PDF/A")
                writeup.generatePDF(html=True)
            # Get reduced html
            if self._html:
                self._logMessage("Creating HTML")
                writeup.generateHTML()

            writeup.texFile = "finalTEX/" + writeup.texFile
            os.system('mv aux.tex ../{0}'.format(writeup.texFile))

            #Copying files to public place
            os.system('scp -P 3121 ../{0} cernlib@cernlib-share:/home/cernlib/ShortWriteUps/PDF/.'.format(writeup.pdfFile))
            writeup.pdfFile = 'http://cernlib-share/code/ShortWriteUps/PDF/{0}'.format(writeup.pdfFile.split('/')[-1])
            os.system('scp -P 3121 ../{0} cernlib@cernlib-share:/home/cernlib/ShortWriteUps/HTML/.'.format(writeup.htmlFile))
            writeup.htmlFile = 'http://cernlib-share/code/ShortWriteUps/HTML/{0}'.format(writeup.htmlFile.split('/')[-1])
            os.system('scp -P 3121 ../{0} cernlib@cernlib-share:/home/cernlib/ShortWriteUps/HTML/.'.format(writeup.reducedHTMLFile))
            writeup.reducedHTMLFile = 'http://cernlib-share/code/ShortWriteUps/HTML/{0}'.format(writeup.reducedHTMLFile.split('/')[-1])

            # Cleaning files
            self._logMessage("Cleaning auxiliar files")
            os.system('rm {0}/*'.format(auxDir))
            # Saving in database
            if self._persist:
                DataManager.saveShortWriteUp(writeup)
        # Sending signal when finished
        self.emit(QtCore.SIGNAL('backProcessFinished()'))


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
