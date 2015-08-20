#
# Copyright (c) 2015 by Antonio Molina García-Retamero. All Rights Reserved.
#

import requests
from bs4 import BeautifulSoup
import shutil
import accents
import re

def mapTexToUnicode(text):
    for accent in accents.latexAccents:
        rex = accent[1]
        text = text.replace(rex, accent[0])
    return text

def getFixedHTML(url):
    html = requests.get(url).text
    r = requests.post("http://fixmyhtml.com/", data = {'html':html})
    soup = BeautifulSoup(r.text, 'html.parser')
    # print(soup.find('textarea', class_='results').get_text())
    return soup.find('textarea', class_='results').get_text()

def getLongWriteUps():
    r = requests.get("http://goossens.web.cern.ch/goossens/cernliblong.html")
    soup = BeautifulSoup(r.text, 'html.parser')
    links = 0
    for dt in soup.dl.children:
        if dt.name == 'dt':
            for link in dt.children:
                if link.name == 'a' and link.get_text() == 'PDF':
                    urlDoc = "/goossens/" + link['href'][2:]
                    print('I have a link', urlDoc)
                    title = dt.next_sibling.next_sibling.get_text().strip()
                    r =requests.get('http://goossens.web.cern.ch'+urlDoc, stream=True)
                    with open('longDocs/'+urlDoc.split('/')[-1], 'wb') as out_file:
                            shutil.copyfileobj(r.raw, out_file)
                    links += 1
    print('I have got {0} links to pdf'.format(links))

# String processing functions

def isPunct(w):
    return re.match(r'^\W+$', w) != None

def histogram(words):
    freq = {}
    for w in words:
        if freq.has_key(w):
            freq[w] = freq[w] + 1
        else:
            freq[w] = 1
    return freq



if __name__ == '__main__':
    # getFixedHTML("http://goossens.web.cern.ch/goossens/wwwdir/shortwrupsdir/b002/top.html")
    getLongWriteUps()
