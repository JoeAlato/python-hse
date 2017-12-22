#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib.request

try:
    from urllib.request import Request, urlopen  # Python 3
except:
    from urllib2 import Request, urlopen  # Python 2
import gzip

headers = {'Accept-Encoding':
               'gzip, deflate', 'accept': '*/*',
           'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
url = 'http://www.dorev.ru/ru-faq-yatroots.html'
req = Request(url, headers=headers)
with urllib.request.urlopen(req) as response:
    html = response.read()
    if (response.headers['content-encoding'] == 'gzip'):
        html = gzip.decompress(html)
print(html[2000:3000])