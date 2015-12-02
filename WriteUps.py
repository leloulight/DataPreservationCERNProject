#
# Copyright (c) 2015 by Antonio Molina García-Retamero. All Rights Reserved.
#

from sqlalchemy import Table, Column, Integer, ForeignKey, String, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import select

from abc import ABCMeta
from PyQt4 import QtCore

import auxTools
import re
import os
import logging
import json

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
    rdef = Column(String) # User Entry name of the documented function.
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
        self.rdef = ""


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
        os.chdir(os.path.dirname(os.path.realpath(__file__))) #TODO: Do this in a more convenient way
        os.system('cp {0} {1}'.format(self.filename, "aux/" + self.texFile))
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

        #Copying files to public place
        os.system('scp -P 3121 ../{0} cernlib@cernlib-share:/home/cernlib/ShortWriteUps/PDF/.'.format(self.pdfFile))
        self.pdfFile = 'http://cernlib-share/code/ShortWriteUps/PDF/{0}'.format(self.pdfFile.split('/')[-1])
        os.system('scp -P 3121 ../{0} cernlib@cernlib-share:/home/cernlib/ShortWriteUps/HTML/.'.format(self.htmlFile))
        self.htmlFile = 'http://cernlib-share/code/ShortWriteUps/HTML/{0}'.format(self.htmlFile.split('/')[-1])
        os.system('scp -P 3121 ../{0} cernlib@cernlib-share:/home/cernlib/ShortWriteUps/HTML/.'.format(self.reducedHTMLFile))
        self.reducedHTMLFile = 'http://cernlib-share/code/ShortWriteUps/HTML/{0}'.format(self.reducedHTMLFile.split('/')[-1])

        # Cleaning files
        logger.info("Cleaning auxiliar files")
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.system('rm aux/*')


    def generatePDF(self, html=False, nonStopMode=True):
        self._generateTemplate() # Generating template with metadata
        if nonStopMode:
            os.system('pdflatex -interaction=nonstopmode aux.tex')
        else :
            os.system('pdflatex aux.tex')
        self.pdfFile = 'finalPDF/' + self.filename.split('/')[-1].replace('tex', 'pdf')
        os.system('mv aux.pdf ../{0}'.format(self.pdfFile))

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


    def getLightJSON(self):
        json = '{'
        json += '"ID" : "{0}",'.format(self.ID)
        json += '"name" : "{0}",'.format(self.name)
        json += '"reducedHTMLFile" : "{0}",'.format(self.reducedHTMLFile)
        json += '"rdef" : "{0}"'.format(" ".join(self.rdef))
        json +='}'

        return json

    def getFullJSON(self):
        json = '{'
        json += '"ID" : "{0}",'.format(self.ID)
        json += '"name" : "{0}",'.format(self.name)
        json += '"version" : "{0}",'.format(self.version)
        json += '"keywords" : "{0}",'.format(self.keywords)
        json += '"library" : "{0}",'.format(self.library)
        json += '"submitter" : "{0}",'.format(self.submitter)
        json += '"submitted" : "{0}",'.format(self.submitted)
        json += '"language" : "{0}",'.format(self.language)
        json += '"revised" : "{0}",'.format(self.revised)
        json += '"pdfFile" : "{0}",'.format(self.pdfFile)
        json += '"htmlFile" : "{0}",'.format(self.htmlFile)
        json += '"reducedHTMLFile" : "{0}",'.format(self.reducedHTMLFile)
        json += '"rdef" : "{0}"'.format(" ".join(self.rdef))
        json +='}'
        return json

    def __str__(self):
        swuStr = "ID: {0}\nName: {1}".format(self.ID, self.name)
        swuStr += '\nKeywords: {0}'.format(self.keywords)
        swuStr += "\nSubmitter: {0}\nSubmitted: {1}\nLanguage: {2}\nRevised: {3}\nRdef: {4}".format(self.submitter, self.submitted, self.language, self.revised, self.rdef)
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
            shortWriteUp.rdef = re.findall(r'\\Rdef{(.*?)}', tex)
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
        os.chdir(os.path.dirname(os.path.realpath(__file__))) #TODO: Do this in a more convenient way
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
        self.pdfFile = ".".join(self._auxMainFile.split('/')[-1].split('.')[0:-1]) + ".pdf"
        print(self.pdfFile)

    def generateHTML(self, inyectShortDoc):
        if self.pdfFile is None:
            self.generatePDF()
        os.system("pdf2htmlEX {0}".format(self.pdfFile))
        self.htmlFile = ".".join(self._auxMainFile.split('/')[-1].split('.')[0:-1]) + ".html"
        if inyectShortDoc:
            fHtml = open(self.htmlFile, 'r+')
            with fHtml:
                html = fHtml.read()
                fHtml.close()
            # Looking for function names apparition, adding mark and data and generate json
            encontrada = 0
            shortLibraryJSON = '['
            # Puedo, por cada funcion, add una entrada para generar todo lo necesario primero y luego inyectarlo
            for swu in DataManager.getShortLibrary():
                for ref in swu.rdef:
                    # Testing way for finding references
                    if ref != '':
                        it = re.finditer(r'\b{0}\b'.format(ref), html)
                        for el in it:
                            print("Encontrado elemento: " + el.group(0) + ' from {0} to {1}'.format(str(el.start()), str(el.end())))
                            # If it is considered a function call
                            html = html[:el.start()] + '<span onmouseover="onLinkOver(this)" data-fname="{1}" class="{0}">{1}</span>'.format("swuLink", ref) + html[el.end():]
                    if ref != '' and ' ' + ref + ' ' in html: # TODO: I have to look for all appearances
                        encontrada += 1
                        print("Encontrada: " + ref)
                        # Sustituyo el texto por el texto en un spam con la clase css y el data necesario
                        # Puedo generar un json de los swu y los inyecto. Luego, con js, recorro el json generando los popups
                        # Inyecting HTML for js manipulation
                        # TODO: I'm working in improving this
                        html = html.replace(ref,
                            '<span onmouseover="onLinkOver(this)" data-fname="{1}" class="{0}">{1}</span>'.format(
                                "swuLink", ref))
                        shortLibraryJSON +='{0},'.format(swu.getJSON())
            print("Encontradas : " + str(encontrada))
            shortLibraryJSON = shortLibraryJSON[0:-1] # take out the last coma
            shortLibraryJSON += ']'


            # Inyecting dependencies
            print("Inyectando dependencias")
            html = html.replace("<title></title>",
                '\n<!-- Dependecies for short doc library documentation -->\n'
                + '<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js"></script>\n'
                + '<script src="../../templates/shortdoc.js"></script>\n'
                + '<script>var shortLibrary = JSON.parse(\'{0}\');</script>\n'.format(shortLibraryJSON)
                + '<title>{0}</title>\n'.format(self.title) # Writeup title
                )
            with open(self.htmlFile, 'w+') as fHtml:
                fHtml.write(html)
                fHtml.close()


    def getHyperSetup(self):
        hypersetup = "\n% PDF/A packages\n"
        hypersetup += "\\usepackage[pdftex, pdfa, linktoc=none]{hyperref}\n"
        hypersetup += "\\hypersetup{\n"
        hypersetup += '\tpdftitle={'+self.title+'}\n'
        hypersetup += '\tpdfauthor={'+self.author+'},\n'
        hypersetup += '\tpdfsubject={CERN Program Library Documentation},\n'
        # hypersetup += '\tpdfkeywords={'+self.keywords+'},\n'
        hypersetup += '\tpdflang={en},\n'
        hypersetup += '\tbookmarksopen=true,\n'
        hypersetup += '\tbookmarksopenlevel=3,\n'
        hypersetup += '\thypertexnames=false,\n'
        hypersetup += '\tlinktocpage=true,\n'
        hypersetup += '\tplainpages=false,\n'
        hypersetup += '\tbreaklinks\n'
        hypersetup += '}\n'

        return hypersetup

class ShortDocInyector(QtCore.QThread):
    def __init__(self, lwu, shortlib):
        QtCore.QThread.__init__(self)
        self.lwu = lwu
        self.shortlib = shortlib

    def run(self):
        # Getting the HTML
        fHtml = open(self.lwu.htmlFile, 'r+')
        with fHtml:
            html = fHtml.read()
            fHtml.close()
        # Looking for function names apparition, adding mark and data and generate json
        encontrada = 0
        shortLibraryJSON = '['
        # Puedo, por cada funcion, add una entrada para generar todo lo necesario primero y luego inyectarlo
        for swu in self.shortlib:
            for ref in swu.rdef:
                if ref in html: # If the name of the function appears
                    encontrada += 1
                    print("Encontrada: " + ref)
                    # Sustituyo el texto por el texto en un spam con la clase css y el data necesario
                    # Puedo generar un json de los swu y los inyecto. Luego, con js, recorro el json generando los popups
                    # Inyecting HTML for js manipulation
                    html = html.replace(ref,
                        '<span onmouseover="onLinkOver(this)" data-fname="{1}" class="{0}">{1}</span>'.format(
                            "swuLink", ref))
                    shortLibraryJSON +='{0},'.format(swu.getJSON())
        print("Encontradas : " + str(encontrada))
        shortLibraryJSON = shortLibraryJSON[0:-1] # take out the las coma
        shortLibraryJSON += ']'

        # Inyecting dependencies
        print("Inyectando dependencias")
        html = html.replace("<title></title>",
            '\n<!-- Dependecies for short doc library documentation -->\n'
            + '<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js"></script>\n'
            + '<script src="../../templates/shortdoc.js"></script>\n'
            + '<script>var shortLibrary = JSON.parse(\'{0}\');</script>\n'.format(shortLibraryJSON)
            + '<title>{0}</title>\n'.format(self.lwu.title) # Writeup title
            )
        with open(self.lwu.htmlFile, 'w+') as fHtml:
            fHtml.write(html)
            fHtml.close()


    def mname(self, arg):
        pass

class DataManager(object):

    def __init__(self):
        super(DataManager, self).__init__()

    @staticmethod
    def saveShortWriteUp(swu):
        session = Session()
        swu.rdef = " ".join(swu.rdef)
        session.add(swu)
        try:
            session.commit()
        except IntegrityError:
            print('Currently it exists a Short writeup with id: {0}'.format(swu.ID))
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
            swuPersisted.rdef = swu.rdef
            swuPersisted.pdfFile = swu.pdfFile
            swuPersisted.htmlFile = swu.htmlFile
            swuPersisted.texFile = swu.texFile
            swuPersisted.reducedHTMLFile = swu.reducedHTMLFile
            session.commit()

    @staticmethod
    def saveLongWriteUp(lwu):
        session = Session()
        session.add(lwu)
        try:
            session.commit()
        except IntegrityError:
            print('Currently it exits a Long writeup which id is: {0}'.format(lwu.ID))
            print('Updating its values')
            session.rollback()
            # Updating the entrance that already exists
            lwuPersisted = session.query(LongWriteUp).filter_by(ID = lwu.ID).first()
            lwuPersisted.title = lwu.title
            lwuPersisted.version = lwu.version
            lwuPersisted.author = lwu.author
            lwuPersisted.copyright = lwu.copyright
            lwuPersisted.texFile = lwu.texFile
            lwuPersisted.pdfFile = lwu.pdfFile
            lwuPersisted.htmlFile = lwu.htmlFile
            session.commit()

    @staticmethod
    def getAllFunctionNames():
        session = Session()
        s = select([ShortWriteUp.rdef])
        result = session.query(ShortWriteUp.rdef)
        fnames = []
        for r in result:
            for rdef in r[0].split(" "):
                fnames.append(rdef)
        return fNames

    @staticmethod
    def getShortByRdef(rdef):
        session = Session()
        swus = session.query(ShortWriteUp)
        for swu in swus:
            swu.rdef = swu.rdef.split(" ")
            for ref in swu.rdef:
                return swu

    @staticmethod
    def getShortLibrary():
        session = Session()
        result = session.query(ShortWriteUp)
        shortLib = []
        for swu in result:
            swu.rdef = swu.rdef.split(" ")
            shortLib.append(swu)
        return shortLib

    @staticmethod
    def getShortLibraryJSON():
        session = Session()
        result = session.query(ShortWriteUp)
        shortLibraryJSON = '['
        for swu in result:
            shortLibraryJSON +='{0},'.format(swu.getFullJSON())
        shortLibraryJSON = shortLibraryJSON[0:-1] + ']'
        return shortLibraryJSON

    @staticmethod
    def initDataBase():
        Base.metadata.create_all(engine)

    @staticmethod
    def deleteDataBase():
        pass # TODO
