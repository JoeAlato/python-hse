# -*- coding: utf-8 -*-
"""python_morphological_analysis_russian

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Q9w8nw55yeq48v13SCaSoq7G7Pf93PTF

# Домашнее задание

**Задание:** Написать веб-сервис (или бота), с которой можно разговаривать: пользователь пишет ей реплику, а она отвечает предложением, в котором все слова заменены на какие-то случайные другие слова той же части речи и с теми же грамматическими характеристиками. Предложение-ответ должно быть согласованным.

Например, на фразу "Мама мыла раму" программа может ответить "Девочка пела песню".

Решение нужно разместить на PythonAnywhere.

Для такой программы вам понадобится большой список русских слов:

можно взять список словоформ с сайта НКРЯ - http://ruscorpora.ru/corpora-freq.html
можно взять просто любой большой текст, вытащить из него слова и использовать их.

Из этого списка вам нужен только список разных лемм разных частей речи, и затем нужно будет использовать функции parse и inflect.

https://github.com/nlpub/pymystem3

https://github.com/nlpub/pymystem3/blob/master/pymystem3/mystem.py

https://tech.yandex.ru/mystem/doc/grammemes-values-docpage/

https://pymorphy2.readthedocs.io/en/latest/
https://pymorphy2.readthedocs.io/en/latest/user/grammemes.html

Установка необходимых библиотек.
"""

!pip install pymorphy2

!pip install pymystem3

"""Скачиваем слова из корпуса русского языка."""

!wget http://ruscorpora.ru/ngrams/1grams-3.zip

!unzip 1grams-3.zip

with open('1grams-3.txt', 'r') as f:
  content = f.readlines()

content[0:10]

content[0].split('\t')[-1].strip()

words = [line.split('\t')[-1].strip() for line in content]

len(words)

len(set(words))

"""# Программа

Импортируем библиотеки.
"""

from pymystem3 import Mystem
import pymorphy2
from pymorphy2 import MorphAnalyzer

"""Создаем экземпляры морфологических парсеров."""

morph = MorphAnalyzer()
m = Mystem()

"""Пример функций Mystem"""

text = 'Мама мыла раму'

ana = m.analyze(text)
print(ana)

lemmas = m.lemmatize(text)
print(lemmas)

"""Пример функций PyMorphy"""

tokens = text.split()
for token in tokens:
  print(morph.parse(token))

for lemma in lemmas:
  print(morph.parse(lemma))

"""Порядок действий:
1. Распарсить входное предложение - получить части речи и остальные грамматические характеристики. (с помощью pymorphy)
2. Выбрать случайную лемму той же части речи для каждого слова.
3. Применить к каждой лемме inflect с входными грамматическими характеристиками.

Получаем теги частеречной разметки Mystem для каждого слова.
"""

pos_tags = []
for an in ana:
  if 'analysis' in an.keys():
    pos_tags.append(an['analysis'][0]['gr'].split(',')[0])
print(pos_tags)

"""Нам нужно уметь выбирать новое случайное слово заданной части речи. Для этого необходимо соответствие между словами корпуса и частеречными тегами.
Создаем словарь, где ключами будут части речи, а значениями - принадлежещие им слова.
"""

word_pos_dict = {}
num_words = 10000
for i, word in enumerate(words[:num_words]):
  print(i, end = '\r')
  word = m.lemmatize(word)[0]
  ana = m.analyze(word)
  if 'analysis' in ana[0].keys():
    if len(ana[0]['analysis']) > 0:
      pos_tag = ana[0]['analysis'][0]['gr'].split(',')[0]
      if '=' in pos_tag:
        pos_tag = pos_tag.split('=')[0]
      if pos_tag in word_pos_dict.keys():
        word_pos_dict[pos_tag] = word_pos_dict[pos_tag] + [word]
      else:
        word_pos_dict[pos_tag] = [word]

print('Количество слов:', sum([len(x)  for x in word_pos_dict.values()]))

word_pos_dict.keys()

"""Фильтруем по длине, чтобы исключить однобуквенные слова, оставшиеся после автоматической обработки инициалов, аббревиатур и т.п."""

candidates_pos = {}
for key, val in word_pos_dict.items():
  if key != 'PART' and key != 'PR' and key != 'SPRO':
    candidates_pos[key] = [x for x in set(val) if len(x) > 1]
  else:
    candidates_pos[key] = set(val)

m = Mystem()
for key, val in candidates_pos.items():
  non_changeable = []
  changeable = []
  for x in val:
    an = m.analyze(x)[0]
    non_changeable_current, changeable_current = an['analysis'][0]['gr'].split('=')
    if '|' in changeable_current:
      changeable_current = changeable_current.replace('(', '').replace(')', '').split("|")[0]
    non_changeable.extend(non_changeable_current.split(','))
    changeable.extend(changeable_current.split(','))
  print(key)
  print('изменяемые:', set(changeable))
  print('неизменяемые:', set(non_changeable))

"""Разбиваем существительные также по одушевлённости (од/неод) и роду (муж/жен/cред), используя Mystem. Это нужно для выбора слов не только по частями речи, но и по другим грамматическим характеристикам.
 Обрати внимание - здесь ключом является не одно значение, а два - одушевлённость и род. Можно представить этот как двумерный словарь-таблицу.
 Отдельно выделяем имена, фамилии, отчества и географические названия.
"""

named_entites = {}
named_entities_labels = ['гео', 'имя', 'фам', 'отч']

def parse_noun(word):
    an = m.analyze(word)[0]
    if 'analysis' in an.keys():
      non_changeable, changeable = an['analysis'][0]['gr'].split('=')
      tags = non_changeable.split(',')
      gender_tag = tags[1]
      if len(tags) > 2:
            anim_tag = tags[2]
      else:
            anim_tag = '-'
    return tags, gender_tag, anim_tag

m = Mystem()
candidates_nouns_grammar = {}
for i, word in enumerate(candidates_pos['S']):
  is_ne = False
  print('Progress: %d / %d' % (i, len(candidates_pos['S'])), end = '\r')
  tags, gender_tag, anim_tag = parse_noun(word)
  for label in named_entities_labels:
      if label in tags:
        named_entites.setdefault(label,[]).append(word)
        is_ne = True
  if not is_ne:
    candidates_nouns_grammar.setdefault((gender_tag, anim_tag),[]).append(word)

print(candidates_nouns_grammar[('жен', 'неод')][:10])

print(candidates_nouns_grammar[('сред', 'неод')][:10])

print(candidates_nouns_grammar[('муж', 'неод')][:10])

print(candidates_nouns_grammar[('муж', 'од')][:10])

"""Глаголы разбиваем аналогичным образом по виду и переходности. Тут можно попробовать оптимизировать код, избавившись от вложённого if-else."""

def parse_verb(word):
    an = m.analyze(word)[0]
    if 'analysis' in an.keys():
      tags = an['analysis'][0]['gr']
      non_changeable, changeable = tags.split('=')
      tags = non_changeable.split(',') + changeable.split(',')
      perf_tag, trans_tag = '-', '-'
      for tag in tags:
        if tag in ['несов', 'сов']:
            perf_tag = tag
        if tag in ['пе', 'нп']:
            trans_tag = tag
    return tags, perf_tag, trans_tag

m = Mystem()
candidates_verbs_grammar = {}
for i, word in enumerate(candidates_pos['V']):
  print('Progress: %d / %d' % (i, len(candidates_pos['V'])), end = '\r')
  tags, perf_tag, trans_tag = parse_verb(word)
  candidates_verbs_grammar.setdefault((perf_tag, trans_tag),[]).append(word)

"""Пример содержания получившегося словаря."""

print(candidates_verbs_grammar[('сов', 'пе')][:10])

print(candidates_verbs_grammar[('сов', 'нп')][:10])

print(candidates_verbs_grammar[('несов', 'пе')][:10])

print(candidates_verbs_grammar[('несов', 'нп')][:10])

"""Разбиваем местоимения по роду, лицу, одушевлённости и числу (если они не указаны, ставим прочерк)."""

def parse_pronoun(word):
    an = m.analyze(word)[0]
    if 'analysis' in an.keys():
      non_changeable, changeable = an['analysis'][0]['gr'].split('=')
      tags = non_changeable.split(',')
      gender_tag, person_tag, anim_tag, num_tag = '-', '-', '-', '-'
      for tag in tags:
        if tag in ['муж', 'жен', 'сред']:
            gender_tag = tag
        if '-л' in tag:
            person_tag = tag
        if tag in ['од', 'неод']:
            anim_tag = tag
        if tag in ['мн', 'ед']:
            num_tag = tag
    return tags, person_tag, num_tag, gender_tag, anim_tag

candidates_pronouns_grammar = {}
for i, word in enumerate(candidates_pos['SPRO']):
  print('Progress: %d / %d' % (i, len(candidates_pos['SPRO'])), end = '\r')
  tags, person_tag, num_tag, gender_tag, anim_tag = parse_pronoun(word)
  candidates_pronouns_grammar.setdefault((person_tag, num_tag, gender_tag, anim_tag),[]).append(word)

import pickle

pickle.dump(candidates_pos, open('candidates_pos.p', 'wb'))
pickle.dump(candidates_verbs_grammar, open('candidates_verbs_grammar.p', 'wb'))
pickle.dump(candidates_nouns_grammar, open('candidates_nouns_grammar.p', 'wb'))
pickle.dump(candidates_pronouns_grammar, open('candidates_pronouns_grammar.p', 'wb'))
pickle.dump(named_entites, open('named_entites.p', 'wb'))

# candidates_pos = pickle.load(open('candidates_pos.p', 'rb'))

"""Сейчас у нас в словаре хранятся множества слов, а не списки. Исправим (иначе некоторые функции в дальнейшем могут не сработать)."""

candidates_pos = {k: list(v) for k, v in candidates_pos.items()}

from google.colab import files

files.download('named_entites.p')

files.download('candidates_pos.p') 
files.download('candidates_verbs_grammar.p') 
files.download('candidates_nouns_grammar.p')
files.download('candidates_pronouns_grammar.p')

"""Теперь, когда у нас есть структура данных для каждого типа речи, которая позволяет выбирать по нескольким неизменяемым грамматическим признакам, мы можем выбрать оттуда слово.
Для того, чтобы сделать это случайнвм образом, нам нужно использовать функцию choice из библиотеки random.
"""

import random

"""Пример случайного выбора существительного."""

random_word = random.choice(candidates_pos['S'])
print(random_word)

"""Чтобы переключаться между Pymorphy и Mystem, нужно иметь соотношение обозначений граммем. Записываем вручную.

Полный список граммем с пояснениями: https://docs.google.com/spreadsheets/d/18RelfNsp94mevWjq4DAU2ifCPXh-J-xC81lDPxk8xmw/edit?usp=sharing
"""

grammems = {"наст": "pres",
"непрош": "pres",
"прош": "past",
"им": "nomn",
"род": "gent",
"дат": "datv",
"вин": "accs",
"твор": "ablt",
"пр": "loct",
"парт": "gen2",
"местн": "loc2",
"зват": "voct",
"ед": "sing",
"мн": "plur",
"деепр": "GRND",
"инф": "INFN",
"прич": "PRT",
"изъяв": "indc",
"пов": "impr",
"притяж": "Poss",
"прев": "Supr",
"срав": "Cmp2",
"муж": "masc",
"жен": "femn",
"сред": "neut",
"несов": "impf",
"сов": "perf",
"действ": "actv",
"страд": "pssv",
"од": "anim",
"неод": "inan",
"пе": "tran",
"нп": "intr",
"1-л": "1per",
"2-л": "2per",
"3-л": "3per"}

"""Наконец, пишем полную функцию, которая принимает на вход текст, разбивает его на слова и анализирует с помощью Mystem, затем выбирает случайное слово нужной части речи и с нужными характеристиками и, наконец, копирует изменяемые грамматические признаки из слов оригинала в слова нашего сгенерированного предложения."""

def choose_random_word(possible_values):
    return random.choice(possible_values)

def mystem2pymorphy(mystem_grammems):
    pymorphy_grammems = [grammems[x] for x in mystem_grammems if x in grammems.keys()]
    if 'кр' in mystem_grammems:
        pymorphy_grammems = [x if x not in ['PRT', 'ADJ'] else x + 'S' for x in pymorphy_grammems]
    if 'полн' in mystem_grammems:
        pymorphy_grammems = [x if x not in ['PRT', 'ADJ'] else x + 'F' for x in pymorphy_grammems]
    return set(pymorphy_grammems)

def generate_response(text, verbose=True):
    # морфологический разбор текста Mystem'ом
    ana = m.analyze(text)

    if verbose:
        print(ana)

    changed_words = []

    for an in ana:
        word = an['text']
        if 'analysis' in an.keys():
            non_changeable, changeable = an['analysis'][0]['gr'].split('=')
            changeable = changeable.replace("(", "").replace(")", "")
            tags = non_changeable.split(',')
            if '|' in changeable:
                changeable = changeable.split("|")[0]
            pos_tag = tags[0]
            grammems_to_change = changeable.split(',')

            if verbose:
                print("POS tag:", pos_tag)

            if pos_tag == 'S':
                is_ne = False
                tags, gender_tag, anim_tag = parse_noun(word)
                for label in named_entities_labels:
                    if label in tags:
                        possible_values = named_entites[label]
                        is_ne = True
                if not is_ne:
                    possible_values = candidates_nouns_grammar[(gender_tag, anim_tag)]
            elif pos_tag == 'V':
                tags, perf_tag, trans_tag = parse_verb(word)
                possible_values = candidates_verbs_grammar[(perf_tag, trans_tag)]
            elif pos_tag == 'SPRO':
                tags, person_tag, num_tag, gender_tag, anim_tag = parse_pronoun(word)
                possible_values = candidates_pronouns_grammar[(person_tag, num_tag, gender_tag, anim_tag )]
            elif pos_tag == 'PR':
                possible_values = [word]
            else:
                possible_values = candidates_pos[pos_tag]

            random_word = choose_random_word(possible_values)
            if verbose:
                print('Random word:', random_word)
                
            parsed = morph.parse(random_word)[0]
            if verbose:
                print('Grammems to change:', grammems_to_change)
            if len(grammems_to_change) > 0:
                try:
                    inflected_word = parsed.inflect(mystem2pymorphy(grammems_to_change)).word
                except Exception as e:
                    random_word = choose_random_word(possible_values)
                    parsed = morph.parse(random_word)[0]
                    if verbose:
                        print('Random word:', random_word)
                    inflected_word = parsed.inflect(mystem2pymorphy(grammems_to_change)).word
            else:
                inflected_word = word
        else:
            inflected_word = word
            
        if word[0].isupper():
            inflected_word = inflected_word.capitalize()
            
        changed_words.append(inflected_word)
        
    response = ''.join(changed_words)
    if verbose:
        print('Response:', response)

    return response

"""Тестируем функцию."""

m = Mystem()
text = 'Мама мыла раму'

generate_response(text)

text = 'Мышь ждала сыр'
response = generate_response(text, False)
print(response)

m.analyze(text)

text = 'Рыцарь стоял на страже'
response = generate_response(text, False)
print(response)

text = 'Кто-то стучит из-за стены'
response = generate_response(text, False)
print(response)

text = 'Я есть царь'
response = generate_response(text, False)
print(response)

text = 'Я из Британии'
response = generate_response(text, False)
print(response)

text = 'Он пришёл по Арбату'
response = generate_response(text, False)
print(response)

text = 'Женившись на ней, он упал'
response = generate_response(text, True)
print(response)

text = 'Женившись на ней, он упал'
response = generate_response(text, True)
print(response)

text = 'Двенадцатого апреля случилось чудо'
response = generate_response(text, True)
print(response)

text = 'Он загодя подошёл к двери'
response = generate_response(text, True)
print(response)

text = 'Рассмеялась буря и понеслись тучи врозь'
response = generate_response(text, True)
print(response)

text = 'И ради ли этого воскрикнула покрасневшая поэтесса "Ах!"'
response = generate_response(text, True)
print(response)

text = 'Свернувшись в клубок, я мерно дышал'
response = generate_response(text, True)
print(response)

"""**Задание:** сделать выбор разбора pyMorphy через разбор Mystem

# Веб-интерфейс

1. Зарегистрироваться на https://pythonanywhere.com
2. Открыть Bash консоль и создать виртуальную переменную. https://help.pythonanywhere.com/pages/VirtualEnvForNewerDjango
3. Установить необходимые библиотеки. https://help.pythonanywhere.com/pages/InstallingNewModules/
4. Указать созданную виртуальную переменную в настройках веб-приложения. https://www.pythonanywhere.com/user/uchido/webapps/#tab_id_uchido_pythonanywhere_com
5. Скачать распакованный корпус и положить его в рабочую директорию веб-приложения.
6. Создать папку templates в рабочей директории веб-приложения и создать там файл index.html с кодом Bootstrap шаблона (можно скопировать исходный код примера: https://getbootstrap.com/docs/4.1/examples/starter-template/)
7. Flask код веб-приложения содержится в flask_app.py

Самое базовое приложение - печатает строчку.
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

"""Добавляем отображение HTML шаблона"""

from flask import render_template
@app.route('/')
def main():
    return render_template('index.html'

"""Добавляем вывод текста

```
        <p>
            {{statement|safe}}
        </p>
```
"""

from flask import render_template
@app.route('/')
def main():
    return render_template('index.html', statement = "Hello!")

"""Добавляем получение текста от пользователя

```
<form method="POST">
  <input name="text">
  <input type="submit">
</form>
```
"""

from flask import request
@app.route('/')
def main():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def main_post():
    statement = request.form['text']
    return render_template('index.html', statement = statement)

"""Добавляем работу с библиотеками."""

from pymystem3 import Mystem
import pymorphy2
from pymorphy2 import MorphAnalyzer
morph = MorphAnalyzer()
m = Mystem()

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def main_post():
    statement = m.analyze(request.form['text'])
    return render_template('index.html', statement = statement)