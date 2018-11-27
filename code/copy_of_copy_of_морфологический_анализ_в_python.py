# -*- coding: utf-8 -*-
from pymystem3 import Mystem
import pymorphy2
from pymorphy2 import MorphAnalyzer

DATA_PATH = "data/"
with open(DATA_PATH + '1grams-3.txt', 'r') as f:
  content = f.readlines()

words = [line.split('\t')[-1].strip() for line in content]

"""Создаем экземпляры морфологических парсеров."""

morph = MorphAnalyzer()
m = Mystem()


pos_tags = []
for an in ana:
  if 'analysis' in an.keys():
    pos_tags.append(an['analysis'][0]['gr'].split(',')[0])
print(pos_tags)


word_pos_dict = {}
for word in words[:1000]:
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

word_pos_dict.keys()

"""Фильтруем по длине, чтобы исключить однобуквенные слова, оставшиеся после автоматической обработки инициалов, аббревиатур и т.п."""

candidates_pos = {}
for key, val in word_pos_dict.items():
  if key != 'PART' and key != 'PR':
    candidates_pos[key] = [x for x in set(val) if len(x) > 1]
  else:
    candidates_pos[key] = set(val)

"""Разбиваем существительные также по одушевлённости (од/неод) и роду (муж/жен/cред), используя Mystem. Это нужно для выбора слов не только по частями речи, но и по другим грамматическим характеристикам.
 Обрати внимание - здесь ключом является не одно значение, а два - одушевлённость и род. Можно представить этот как двумерный словарь-таблицу.
"""

m = Mystem()
candidates_nouns_grammar = {}
for i, word in enumerate(candidates_pos['S']):
  print('Progress: %d / %d' % (i, len(candidates_pos['S'])), end = '\r')
  ana = m.analyze(word)
  for an in ana:
    if 'analysis' in an.keys():
      non_changeable, changeable = an['analysis'][0]['gr'].split('=')
      tags = non_changeable.split(',')
      gender_tag = tags[1]
      anim_tag = tags[2]
      candidates_nouns_grammar.setdefault((gender_tag, anim_tag),[]).append(word)

m = Mystem()
candidates_verbs_grammar = {}
for i, word in enumerate(candidates_pos['V']):
  print('Progress: %d / %d' % (i, len(candidates_pos['V'])), end = '\r')
  ana = m.analyze(word)
  for an in ana:
    if 'analysis' in an.keys():
      tags = an['analysis'][0]['gr']
      if 'несов' in tags:
        if 'пе' in tags:
          candidates_verbs_grammar.setdefault(('несов', 'пе'),[]).append(word)
        else:
          candidates_verbs_grammar.setdefault(('несов', 'нп'),[]).append(word)
      else:
        if 'пе' in tags:
          candidates_verbs_grammar.setdefault(('сов', 'пе'),[]).append(word)
        else:
          candidates_verbs_grammar.setdefault(('сов', 'нп'),[]).append(word)

candidates_pos['SPRO'] = candidates_pos['SPRO'] + ['я']

candidates_pronouns_grammar = {}
for i, word in enumerate(candidates_pos['SPRO']):
  print('Progress: %d / %d' % (i, len(candidates_pos['SPRO'])), end = '\r')
  ana = m.analyze(word)
  for an in ana:
    if 'analysis' in an.keys():
      non_changeable, changeable = an['analysis'][0]['gr'].split('=')
      tags = non_changeable.split(',')
      if len(tags) > 1:
        num_tag = tags[1]
      else:
        num_tag = '-'
      if len(tags) > 2:
        person_tag = tags[2]
      else:
        person_tag = '-'
      candidates_pronouns_grammar.setdefault((person_tag, num_tag),[]).append(word)


candidates_pos = {k: list(v) for k, v in candidates_pos.items()}

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
"прич": "PRTF, PRTS",
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

def generate_response(text, verbose = True):
  # морфологический разбор текста Mystem'ом
  ana = m.analyze(text)
  
  if verbose:
    print(ana)
    
  changed_words = []
  
  for an in ana:
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
        gender_tag = tags[1]
        anim_tag = tags[2]
        random_word = random.choice(candidates_nouns_grammar[(gender_tag, anim_tag)])
      elif pos_tag == 'V':
        if 'несов' in tags:
          if 'пе' in tags:
            random_word = random.choice(candidates_verbs_grammar[('несов', 'пе')])
          else:
            random_word = random.choice(candidates_verbs_grammar[('несов', 'нп')])
        else:
          if 'пе' in tags:
            random_word = random.choice(candidates_verbs_grammar[('сов', 'пе')])
          else:
            random_word = random.choice(candidates_verbs_grammar[('сов', 'нп')])
      elif pos_tag == 'SPRO':
        if len(tags) > 1:
          num_tag = tags[1]
        else:
          num_tag = '-'
        if len(tags) > 2:
          person_tag = tags[2]
        else:
          person_tag = '-'
        random_word = random.choice(candidates_pronouns_grammar[(person_tag, num_tag)])
      else:
        random_word = random.choice(candidates_pos[pos_tag])
      if verbose:
        print('Random word:', random_word)
      prog = morph.parse(random_word)[0]
      if verbose:
        print('Grammems to change:', grammems_to_change)
      changed_words.append(prog.inflect(set([grammems[x] for x in grammems_to_change if x in grammems.keys()])).word)
  
  response = ' '.join(changed_words)
  if verbose:
    print('Response:', response)
  
  return response