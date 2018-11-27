import urllib.request

with urllib.request.urlopen('https://yandex.ru/pogoda/10463?') as response:
    html = response.read()

from bs4 import BeautifulSoup

soup = BeautifulSoup(html, 'html.parser')

temp = -100
for elem in soup.find("div", { "class" : "fact__temp" }):
    if elem['class'][0] == "temp__value":
        temp = elem.text
wind_speed = soup.find("span", { "class" : "wind-speed" }).text
condition = soup.find("div", { "class" : "fact__condition" }).text
