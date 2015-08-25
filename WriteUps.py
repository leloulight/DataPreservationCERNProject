#
# Copyright (c) 2015 by Antonio Molina García-Retamero. All Rights Reserved.
#

from sqlalchemy import Table, Column, Integer, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base

import auxTools
import re
import os
import logging

Base = declarative_base()
logger = logging.getLogger("DataPreservationLogger")

class WriteUp(object):
    """Class representing a long WriteUp. It implements a common persistance mechanism
    for both, short and long writeups."""
    def __init__(self):
        super(WriteUp, self).__init__()

        # Basic PDF/A attributes
        self.title = ''
        self.author = ''
        self.subject = ''
        self.keywords = ''
        self.pdf = ''
        self.html = ''
        self.tex = ''

        # Control Attributes
        self.parsed = False


class ShortWriteUp(Base, WriteUp):
    """Class representing a short writeup that documents a procedure or routine"""

    # Persistent attributes
    __tablename__ = 'ShortWriteUps'
    ID = Column(String, primary_key=True)
    name = Column(String)
    version = Column(String)
    keywords = Column(String)
    library = Column(String)
    submitter = Column(String)
    submitted = Column(String) # TODO: I have to convert it into a Date dataType
    language = Column(String)
    revised = Column(String)
    pdf = Column(String)
    html = Column(String)
    tex = Column(String)


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
        hypersetup = "\\hypersetup{\n"
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
        #TODO: I HAVE TO DO THIS BY INHERITANCE BY GETTING THE PARTICULAR PART SEPARATED
        logger.info("Copying file for processing")
        os.system('cp {0} {1}'.format(self.filename, "aux/" + self.filename.split('/')[-1]))
        # print(swu.getHyperSetup())
        if pdf:
            logger.info("Creating PDF/A")
            self._generatePDF()
        # Get reduced html
        if html:
            logger.info("Creating reduced HTML")
            self._generateHtml()
        # Cleaning files
        logger.info("Cleaning auxiliar files")
        os.system('rm {0}.*'.format(self.filename.split('/')[-1].split('.')[0])) # TODO: It can be improved
        os.system('rm *.png')


    def _generatePDF(self, html=False, nonStopMode=True):
        self._generateTemplate() # Generating template with metadata
        if nonStopMode:
            os.system('pdflatex -interaction=nonstopmode {0}'.format(self.tex))
        else :
            os.system('pdflatex {0}'.format(self.tex))
        self.pdf = 'finalPDF/' + self.filename.split('/')[-1].replace('tex', 'pdf')
        os.system('mv {0} {1}'.format(self.pdf.split('/')[-1], self.pdf))

        if html: # Get final Html from PDF
            # logger.info("Creating funcy HTML")
            os.system('pdf2htmlEX {0}'.format(self.pdf))
            self.html = 'finalHTML/' + self.filename.split('/')[-1].replace('tex', 'html')
            os.system('mv {0} {1}'.format(self.html.split('/')[-1], self.html))

    def _generateTemplate(self, metadata=True):
        self.tex = 'finalTEX/' + self.filename.split('/')[-1]
        fInput = open('ONEONLY.tex', 'r') # Loading template
        tex = fInput.read()
        fInput.close()
        tex = tex.replace('XXXX', self.filename.split('/')[-1].split('.')[0])
        if metadata:
            #TODO: I have to add the usingpackage here.
            tex = tex.replace('XXMetadata', self.getHyperSetup())
        else:
            tex = tex.replace('XXMetadata', "")
        fOutput = open('JUNK.tex', 'w')
        fOutput.write(tex) # Saving processed latex
        fOutput.close()
        os.system('cp JUNK.tex {0}'.format(self.tex))


    def _generateHtml(self, reduced=False):
        # TODO: I have to generate the html without metadata
        self._generateTemplate(metadata=False)
        os.system('htlatex {0}'.format(self.tex))
        #TODO: Copy the reduced html to a separated folder


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
        self.textFile = '{0}.txt'.format(self.name.replace(' ', '-').replace('/', ''))
        f = open('shortDocs/'+self.textFile, 'w')
        with f:
            f.write(soup.get_text().strip())
        # Get the author or create if not exist
        self.author = Author.getAuthorByName(self.authorName)

class LongWriteUp(WriteUp):
    """Class representing a short writeup"""
    def __init__(self):
        super(LongWriteUp, self).__init__()
