#
# Copyright (c) 2015 by Antonio Molina Garcia-Retamero. All Rights Reserved.
#

import sys
import os
from dataManager import ShortWriteUp
#from DataPreservationProcessingGUI import run

def printUsage():
    pass # TODO

def processShortWriteUp(fileName):
    # Include writeup into template
    os.system('cp {0} aux.tex'.format(fileName))
    # Parsing writUp for getting common information and persistance
    swu = ShortWriteUp.parseFromTex('aux.tex')
    print(swu)
    # print(swu.getHyperSetup())
    # Creating latex from template
    swu.tex = 'finalTEX/' + fileName.split('/')[-1]
    fInput = open('ONEONLY.tex', 'r') # Loading template
    tex = fInput.read()
    fInput.close()
    tex = tex.replace('XXXX', 'aux')
    # Get extra information

    # Write metadata
    tex = tex.replace('XXMetadata', swu.getHyperSetup())
    fOutput = open('JUNK.tex', 'w')
    fOutput.write(tex) # Saving processed latex
    fOutput.close()
    os.system('cp JUNK.tex {0}'.format(swu.tex)) # TODO: I've to include the short tex. this one is just the template with its metadata
    # Get html
    # os.system('htlatex JUNK.tex')
    # Compile final PDF/A
    os.system('pdflatex JUNK.tex')
    swu.pdf = 'finalPDF/' + fileName.split('/')[-1].replace('tex', 'pdf')
    os.system('cp JUNK.pdf {0}'.format(swu.pdf))
    # Get final Html from PDF
    os.system('pdf2htmlEX {0}'.format(swu.pdf))
    swu.html = 'finalHTML/' + fileName.split('/')[-1].replace('tex', 'html')
    os.system('cp {0} {1}'.format(swu.pdf.split('/')[-1].replace('pdf', 'html'), swu.html))
    # Cleaning files
    os.system('rm JUNK.*')
    # Persist into database
    ShortWriteUp.add(swu)

def processLongWriteUp(fileName):
    # Include writeup into template
    os.system('cp {0} aux.tex'.format(fileName))
    # Parsing writUp for getting common information and persistance
    swu = ShortWriteUp.parseFromTex('aux.tex')
    print(swu)
    # print(swu.getHyperSetup())
    # Creating latex from template
    fInput = open('ONEONLY.tex', 'r') # Loading template
    tex = fInput.read()
    fInput.close()
    tex = tex.replace('XXXX', 'aux')
    # Get extra information

    # Write metadata
    tex = tex.replace('XXMetadata', swu.getHyperSetup())
    fOutput = open('JUNK.tex', 'w')
    fOutput.write(tex) # Saving processed latex
    fOutput.close()
    # Get html
    # os.system('htlatex JUNK.tex')
    # Compile final PDF/A
    os.system('pdflatex JUNK.tex')
    os.system('cp JUNK.pdf finalPDF/{0}'.format(fileName.split('/')[-1].replace('tex', 'pdf')))
    # Get final Html from PDF
    os.system('pdf2htmlEX finalPDF/{0}'.format(fileName.split('/')[-1].replace('tex', 'pdf')))
    os.system('cp {0} finalHTML/.'.format(fileName.split('/')[-1].replace('tex', 'html')))
    # Cleaning files
    os.system('rm JUNK.*')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Wrong number of parameters")
        printUsage()
        quit()
    if sys.argv[1] == 'short':
        fileName = sys.argv[2]
        print("Processing short WriteUp " + fileName)
        processShortWriteUp(fileName)
    elif sys.argv[1] == 'gui':
        run()
