#
# Copyright (c) 2015 by Antonio Molina García-Retamero. All Rights Reserved.
#

from sqlalchemy import Table, Column, Integer, ForeignKey, String, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import select

from abc import ABCMeta

import auxTools
import re
import os
import logging

Base = declarative_base()
engine = create_engine('sqlite:///DataPreservation.db')
Session = sessionmaker()
Session.configure(bind=engine)

logger = logging.getLogger("DataPreservationLogger")

class WriteUp(object):
    """Class representing a long WriteUp. It implements a common persistance mechanism
    for both, short and long writeups."""
    def __init__(self):
        super(WriteUp, self).__init__()

        # Common
        self.ID = ''
        self.version = ''
        self.pdfFile = ''
        self.htmlFile = ''
        self.texFileFileFile = ''

        # Basic PDF/A attributes
        self.title = ''
        self.author = ''
        self.subject = ''
        self.keywords = ''
        self.pdf = ''
        self.html = ''
        self.texFileFile = ''

        # Control Attributes
        self.parsed = False

        # Abstract methods
        # TODO: I have changed the signature of the methods in the children... So it is not abstract anymore. Think about it
        def createPDF(self): pass
        def createHTML(self): pass


class ShortWriteUp(Base, WriteUp):
    """Class representing a short writeup that documents a procedure or routine"""

    # Persistent attributes
    __tablename__ = 'ShortWriteUps'
    ID = Column(String, primary_key=True) # Document identifier
    name = Column(String) # Name of the function documented
    version = Column(String) # Version of the software. Can be NULL
    keywords = Column(String) # String of keywords
    library = Column(String) # Library of the documented function. Can be NULL
    submitter = Column(String) # Name of the submitter. Can be NULL
    submitted = Column(String) # Date in which it was submitted. Can be NULL
    language = Column(String) # Language in which the documented function was writen. Can be NULL
    revised = Column(String) # Date in which the document was revised. Can be NULL
    pdfFile = Column(String) # URL of the corresponding pdf file
    htmlFile = Column(String) # URL of the corresponding HTML file
    reducedHTMLFile = Column(String) # URL to the corresponding reduced HTML
    texFile = Column(String) # URL to the corresponding LaTeX file


    def __init__(self):
        super(ShortWriteUp, self).__init__()
        self.obsolete = False

        self.filename = ""
        #Attributes from short writeups
        self.version = ""
        self.ID = ""
        self.keywords = ""
        self.authorName = ""
        self.library = ""
        self.submitter = ""
        self.submitted = ""
        self.language = ""
        self.name = ""
        self.revised = ""


    def getHyperSetup(self):
        hypersetup = "\n% PDF/A packages\n"
        hypersetup += "\\usepackage[pdftex, pdfa, linktoc=none]{hyperref}\n"
        hypersetup += "\\hypersetup{\n"
        hypersetup += '\tpdftitle={'+self.name+' - CERN Program Library},\n'
        hypersetup += '\tpdfauthor={'+self.authorName+'},\n'
        hypersetup += '\tpdfsubject={Cern Library Documentation},\n'
        hypersetup += '\tpdfkeywords={'+self.keywords+'},\n'
        hypersetup += '\tpdflang={en},\n'
        hypersetup += '\tbookmarksopen=true,\n'
        hypersetup += '\tbookmarksopenlevel=3,\n'
        hypersetup += '\thypertexnames=false,\n'
        hypersetup += '\tlinktocpage=true,\n'
        hypersetup += '\tplainpages=false,\n'
        hypersetup += '\tbreaklinks\n'
        hypersetup += '}'

        return hypersetup

    def process(self, pdf, html, nonStopMode=True):
        logger.info("Copying file for processing")
        self.texFile = self.filename.split('/')[-1]
        os.system('cp {0} {1}'.format(self.filename, "aux/" + self.texFile))
        if os.getcwd().split('/')[-1] != "aux":
            self._auxDir = os.getcwd() + "/aux"
        os.chdir(self._auxDir)
        # print(swu.getHyperSetup())
        if pdf:
            logger.info("Creating PDF/A")
            self.generatePDF(html=True)
        # Get reduced html
        if html:
            logger.info("Creating reduced HTML")
            self.generateHTML()
        self.texFile = "finalTEX/" + self.texFile
        os.system('mv aux.tex ../{0}'.format(self.texFile))
        # Cleaning files
        logger.info("Cleaning auxiliar files")
        if os.getcwd().split('/')[-1] != "aux":
            self._auxDir = os.getcwd() + "/aux"
        os.system('rm *')


    def generatePDF(self, html=False, nonStopMode=True):
        self._generateTemplate() # Generating template with metadata
        if nonStopMode:
            os.system('pdflatex -interaction=nonstopmode aux.tex')
        else :
            os.system('pdflatex aux.tex')
        self.pdfFile = 'finalPDF/' + self.filename.split('/')[-1].replace('tex', 'pdf')
        os.system('mv aux.pdf {0}'.format("../" + self.pdfFile))

        if html: # Get final Html from PDF
            os.system('pdf2htmlEX ../{0}'.format(self.pdfFile))
            self.htmlFile = 'finalHTML/' + self.texFile.split('.')[0] + ".html"
            os.system('mv {0} ../{1}'.format(self.htmlFile.split('/')[-1], self.htmlFile))

    def _generateTemplate(self, metadata=True):
        fInput = open('../templates/ONEONLY.tex', 'r') # Loading template
        tex = fInput.read()
        fInput.close()
        tex = tex.replace('XXXX', self.texFile.split('.')[0])
        if metadata:
            tex = tex.replace('XXMetadata', self.getHyperSetup())
        else:
            tex = tex.replace('XXMetadata', "")
        fOutput = open('aux.tex', 'w')
        fOutput.write(tex) # Saving processed latex
        fOutput.close()


    def generateHTML(self, reduced=False):
        # TODO: I have to generate the html without metadata
        self._generateTemplate(metadata=False)
        os.system('htlatex aux.tex "xhtml"')

        # TODO: I HAVE TO INSERT THE CSS INTO THE HTML

        self.reducedHTMLFile = 'finalHTML/' + self.texFile.split('.')[0] + "-r.html"
        os.system('mv aux.html ../{0}'.format(self.reducedHTMLFile))


    def __str__(self):
        swuStr = "ID: {0}\nName: {1}".format(self.ID, self.name)
        swuStr += '\nKeywords: {0}'.format(self.keywords)
        swuStr += "\nSubmitter: {0}\nSubmitted: {1}\nLanguage: {2}\nRevised: {3}".format(self.submitter, self.submitted, self.language, self.revised)
        return swuStr

    @staticmethod
    def parseFromTex(filename):
        f = open(filename)
        shortWriteUp = ShortWriteUp()
        shortWriteUp.filename = filename
        with f:
            tex = f.read()
            shortWriteUp.authorName = auxTools.mapTexToUnicode(re.search(r'.*\\Author{(.*?)}', tex).group(1))
            # TODO: After getting authorName I should look for the author in the database
            shortWriteUp.ID = auxTools.mapTexToUnicode(re.search(r'.*\\Routid{(.*?)}', tex).group(1))
            shortWriteUp.keywords = auxTools.mapTexToUnicode(re.search(r'.*\\Keywords{(.*?)}', tex).group(1))
            shortWriteUp.library = auxTools.mapTexToUnicode(re.search(r'.*\\Library{(.*?)}', tex).group(1))
            shortWriteUp.submitter = auxTools.mapTexToUnicode(re.search(r'.*\\Submitter{(.*?)}', tex).group(1))
            shortWriteUp.submitted = auxTools.mapTexToUnicode(re.search(r'.*\\Submitted{(.*?)}', tex).group(1))
            shortWriteUp.language = auxTools.mapTexToUnicode(re.search(r'.*\\Language{(.*?)}', tex).group(1))
            shortWriteUp.name = auxTools.mapTexToUnicode(re.search(r'.*\\Cernhead{(.*?)}', tex).group(1))
        shortWriteUp.parsed = True
        return shortWriteUp

    @staticmethod
    def parseFromHTML(self, soup):
        self.ID = soup.h2.get_text().split(':')[0].strip()
        self.name = soup.h2.get_text().split(':')[1][1:].strip()
        # Info from the table
        rows = soup.findAll('tr')
        print(list(rows[1].children)[1].get_text().split(':')[1][1:])
        self.authorName = list(rows[0].children)[1].get_text().split(':')[1][1:].strip()
        self.library = list(rows[0].children)[3].get_text().split(':')[1][1:].strip()
        self.submitter = list(rows[1].children)[1].get_text().split(':')[1][1:].strip()
        self.submitted = list(rows[1].children)[3].get_text().split(':')[1][1:].strip()
        self.language = list(rows[2].children)[1].get_text().split(':')[1][1:].strip()
        self.revised = list(rows[2].children)[3].get_text().split(':')[1][1:].strip()
        # Description at the begining
        print(soup.table.nextSibling.nextSibling.nextSibling.nextSibling.get_text())
        # Getting the HTML body text and storing into text file
        self.texFileFiletFile = '{0}.txt'.format(self.name.replace(' ', '-').replace('/', ''))
        f = open('shortDocs/'+self.texFileFiletFile, 'w')
        with f:
            f.write(soup.get_text().strip())
        # Get the author or create if not exist
        self.author = Author.getAuthorByName(self.authorName)

class LongWriteUp(Base, WriteUp):
    """Class representing a short writeup"""

    # Persistent attributes
    __tablename__ = 'LongWriteUps'
    ID = Column(String, primary_key=True) # Document ID
    title = Column(String) # Title of the documented writeup
    version = Column(String) # Version of the documentation
    author = Column(String) # Name of the author
    copyright = Column(String) # Date of the copyright
    texFile = Column(String) # URL to the corresponding LaTeX file
    pdfFile = Column(String) # URL to the corresponding pdf file
    htmlFile = Column(String) # URL to the corresponding HTML file

    def __init__(self):
        super(LongWriteUp, self).__init__()
        self.ID = ''
        self.title = ''
        self.version = ''
        self.author = ''
        self.copyright = ''
        self.texFileFileFile = ''
        self.pdfFile = ''
        self.htmlFile = ''

    def __init__(self, id, title, version, contact, copyright, texFile):
        super(LongWriteUp, self).__init__()
        self.ID = id
        self.title = title
        self.version = version
        self.author = contact
        self.copyright = copyright
        self.texFileFileFile = texFile
        self.pdfFile = ''
        self.htmlFile = ''

    def process(self, pdf, html, inyectShortDoc, nonStopMode=True):
        logger.info("Copying file for processing")
        self._fDir = "/".join(self.texFileFileFile.split('/')[0:-1])
        self._auxDir = os.getcwd() + "/aux/" + self.ID
        self._auxMainFile = self._auxDir + "/" + self.texFileFileFile.split('/')[-1]
        os.system('mkdir {0} && cd {0}'.format(self._auxDir))
        logger.info("Getting all files from: " + self._fDir)
        os.system('cp -r {0}/* {1}/.'.format(self._fDir, self._auxDir))

        if pdf:
            logger.info("Creating PDF/A")
            self.generatePDF()
        # Get reduced html
        if html:
            logger.info("Creating HTML from PDF")
            self.generateHTML(inyectShortDoc)
        # # Cleaning files
        # logger.info("Cleaning auxiliar files")
        # os.system('rm {0}.*'.format(self.filename.split('/')[-1].split('.')[0])) # TODO: It can be improved
        # os.system('rm *.png')

    def generatePDF(self):
        # Inyecting the PDF/A Package and metadata
        mainTexFile = open(self._auxMainFile, 'r')
        mainTex = mainTexFile.read().split('\n')
        mainTexFile.close()
        os.system("rm -f {0}".format(self._auxMainFile))# Removing file for avoiding problems with permissions
        for n, line in enumerate(mainTex):
            # Placing the metadata befor the index. I expect it were fine
            if re.search(r'.*\\makeindex', line) is not None:
                mainTex[n] = self.getHyperSetup() + "\n" + line
                break

        mainTex = "\n".join(mainTex)
        mainTexFile = open(self._auxMainFile, 'w')
        mainTexFile.write(mainTex)
        mainTexFile.close()
        # Generate PDF/A and saving it
        os.chdir(self._auxDir)
        os.system("pdflatex -interaction=nonstopmode {0}".format(self._auxMainFile))
        # Save the pdf file to a final place and save the pointing variable
        self._pdfFile = ".".join(self._auxMainFile.split('/')[-1].split('.')[0:-1]) + ".pdf"
        print(self._pdfFile)

        pass

    def generateHTML(self, inyectShortDoc):
        if self._pdfFile is None:
            self.generatePDF()
        os.system("pdf2htmlEX {0}".format(self._pdfFile))
        if inyectShortDoc:
            # Getting the reducedHTML
            # TODO: I have to get all the functions name and look if they appears on the document
            functions = DataManager.getAllFunctionsName()
            # Inyecting the scripts and the documentation

    def getHyperSetup(self): #TODO: Esto lo tengo que hacer bien...
        hypersetup = "\n% PDF/A packages\n"
        hypersetup += "\\usepackage[pdftex, pdfa, linktoc=none]{hyperref}\n"
        hypersetup += "\\hypersetup{\n"
        hypersetup += '\tpdftitle={'+self.title+' - CERN Program Library},\n'
        hypersetup += '\tpdfauthor={'+self.author+'},\n'
        hypersetup += '\tpdfsubject={Cern Library Documentation},\n'
        hypersetup += '\tpdfkeywords={'+self.copyright+'},\n' #TODO: Chapuza por arreglar
        hypersetup += '\tpdflang={en},\n'
        hypersetup += '\tbookmarksopen=true,\n'
        hypersetup += '\tbookmarksopenlevel=3,\n'
        hypersetup += '\thypertexnames=false,\n'
        hypersetup += '\tlinktocpage=true,\n'
        hypersetup += '\tplainpages=false,\n'
        hypersetup += '\tbreaklinks\n'
        hypersetup += '}\n'

        return hypersetup

class DataManager(object):

    def __init__(self):
        super(DataManager, self).__init__()

    @staticmethod
    def saveShortWriteUp(swu):
        session = Session();
        session.add(swu)
        try:
            session.commit()
        except IntegrityError:
            print('Currently exist a short write up with id: {0}'.format(swu.ID))
            print('Updating its values')
            session.rollback()
            # Updating the entrance that already exists
            swuPersisted = session.query(ShortWriteUp).filter_by(ID = swu.ID).first()
            swuPersisted.name = swu.name
            swuPersisted.version = swu.version
            swuPersisted.keywords = swu.keywords
            swuPersisted.library = swu.library
            swuPersisted.submitter = swu.submitter
            swuPersisted.submitted = swu.submitted
            swuPersisted.language = swu.language
            swuPersisted.revised = swu.revised
            swuPersisted.pdfFile = swu.pdfFile
            swuPersisted.htmlFile = swu.htmlFile
            swuPersisted.texFile = swu.texFile
            swuPersisted.reducedHTMLFile = swu.reducedHTMLFile
            session.commit()

    @staticmethod
    def saveLongWriteUp(lwu):
        pass

    @staticmethod
    def getAllFunctionsName():
        print("Looking for those functions")

        pass

    @staticmethod
    def initDataBase():
        Base.metadata.create_all(engine)

    @staticmethod
    def deleteDataBase():
        pass # TODO
