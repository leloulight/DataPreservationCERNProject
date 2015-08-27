#
# Copyright (c) 2015 by Antonio Molina Garcia-Retamero. All Rights Reserved.
#


from bs4 import BeautifulSoup
from unicode_tex import tex_to_unicode
import sqlite3 as lite
import auxTools
import http.client
import auxTools
import re

from sqlalchemy import Table, Column, Integer, ForeignKey, String, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError

from WriteUps import WriteUp, ShortWriteUp, LongWriteUp

Base = declarative_base()
engine = create_engine('sqlite:///DataPreservation.db')
Session = sessionmaker()
Session.configure(bind=engine)



class NoAuthorExistException(Exception):
    def __init__(self, message):
        self.message = message


class Reference(object):
    """Class representing a reference for long and short writeups"""
    def __init__(self):
        super(Reference, self).__init__()

    def loadFromShort(string):
        pass


class Author(Base):
    """Model class for storing and retreaving authors"""

    __tablename__ = "Authors"
    idAuthor = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, idAuthor, name):
        super(Author, self).__init__()
        self.idAuthor = idAuthor
        self.name = name

    @staticmethod
    def insertAuthor(name):
        con = lite.connect('docuTest.db')
        with con:
            cur = con.cursor()
            query = 'INSERT INTO Author(Name) VALUES ("{0}");'.format(name)
            cur.execute(query)
            return Author(cur.lastrowid, name)

    @staticmethod
    def getAuthorById(idAuthor):
        con = lite.connect('docuTest.db')
        with con:
            cur = con.cursor()
            query = 'SELECT Name FROM Author WHERE AuthorId = {0};'.format(idAuthor)
            cur.execute(query)
            print(cur.fetchall()) # TODO: Acabar esto

    @staticmethod
    def getAuthorByName(authorName):
        con = lite.connect('docuTest.db')
        with con:
            cur = con.cursor()
            query = 'SELECT * FROM Author WHERE Author.name = "{0}";'.format(authorName)
            cur.execute(query)
            authors = cur.fetchall()
            if len(authors) < 1:
                return Author.insertAuthor(authorName)
            else:
                return Author(authors[0][0], authors[0][1])

    def __str__(self):
        authorStr = "Name: {0}".format(self.name)
        return authorStr

# Data relationships
association_table = Table('association', Base.metadata,
    Column('writeup_id', String, ForeignKey(ShortWriteUp.ID)),
    Column('author_id', Integer, ForeignKey(Author.idAuthor))
)

def initAlchemy():
    Base.metadata.create_all(engine)


def testSinglePaper():
    doc = BeautifulSoup(auxTools.getFixedHTML("http://goossens.web.cern.ch/goossens/wwwdir/shortwrupsdir/b002/top.html"), 'html.parser')
    proc = ShortWriteUp()
    proc.loadFromHTML(doc)
    print(proc)
    # ShortWriteUp.insertShortWriteup(proc)


def getDocFromWeb():
    #Find for the short writeups
    conn = http.client.HTTPConnection("goossens.web.cern.ch")
    conn.request("GET", "/goossens/cernlibshort.html")
    soup = BeautifulSoup(conn.getresponse().read(), 'html.parser')

    #Fill the information from each of them and store it
    for cat in soup.find_all('h2'):
        if re.match("[A-Z]", cat.get_text()):
            print("Got a category:")
            print(cat.get_text())
            print("Getting documents on it:")
            if cat.next_sibling.next_sibling and cat.next_sibling.next_sibling.name == "dl":
                dl = cat.next_sibling.next_sibling
                for dt in dl.children:
                    if dt.name == "dt":
                        urlDoc = "/goossens/" + dt.a['href'][2:] # Here i got the html link
                        print("Getting link to html doc at:", urlDoc)
                        # conn = http.client.HTTPConnection("goossens.web.cern.ch")
                        doc = BeautifulSoup(auxTools.getFixedHTML('http://goossens.web.cern.ch'+urlDoc), 'html.parser')
                        print("Parsing:", doc.title.get_text())
                        proc = ShortWriteUp()
                        proc.loadFromHTML(doc)
                        ShortWriteUp.insertShortWriteup(proc)
                        print(proc)

if __name__ == '__main__':
    # initDataBase()
    # insertAuthor('Antonio')
    # getAuthor(1)
    # print(Author.getAuthorByName("Antonio"))
    # testSinglePaper()
    # getDocFromWeb()
    pass
