import urllib.request
from bs4 import BeautifulSoup

req = urllib.request.Request('http://wiki.dothraki.org/Vocabulary', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read()
soup = BeautifulSoup(html, 'html.parser')
words = soup.select('ul li b')
pos = []
for i in soup.select('dl'):
    pos.append(i.find('dd').find('i').text)