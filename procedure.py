
from bs4 import BeautifulSoup
import http.client
import re
from auxTools import getFixedHTML



def getPaper():
    conn = http.client.HTTPConnection("goossens.web.cern.ch")
    conn.request("GET", "/goossens/wwwdir/shortwrupsdir/b002/top.html")
    f = open('PaperCopy.html', 'w')
    f.write(conn.getresponse().read().decode("utf-8"))
    f.close()

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
                        doc = BeautifulSoup(getFixedHTML(urlDoc), 'html.parser')
                        print("Parsing:", doc.title.get_text())
                        proc = Procedure()
                        proc.loadFromHTML(doc)
                        print(proc)

def testProcLoadingFromFile():
    f = open('PaperCopy.html', 'r')
    soup = BeautifulSoup(f.read(), 'html.parser')
    proc = ShortWriteUp()
    proc.loadFromHTML(soup)

if __name__ == '__main__':
    # getPaper()
    # getDocFromWeb()
    # testProcLoadingFromFile()
    testSinglePaper()
