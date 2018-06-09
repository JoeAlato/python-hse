# -*- coding: utf-8 -*-
from pymystem3 import Mystem
from pymorphy2 import MorphAnalyzer
import pickle

morph = MorphAnalyzer()
m = Mystem()

DATA_PATH = "/home/kaprushka/mysite/data/"
print('Loading wordlist.')
with open(DATA_PATH + '1grams-3.txt', 'r') as f:
  content = f.readlines()
words = [line.split('\t')[-1].strip() for line in content]
word_pos_dict = {}
num_words = 10000


"""Нам нужно уметь выбирать новое случайное слово заданной части речи.
   Для этого необходимо соответствие между словами корпуса и частеречными тегами.
   Создаем словарь, где ключами будут части речи, а значениями - принадлежещие им слова."""

print('Creating POS - word dictionary.')
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

"""Фильтруем по длине, чтобы исключить однобуквенные слова,
   оставшиеся после автоматической обработки инициалов, аббревиатур и т.п."""

candidates_pos = {}
for key, val in word_pos_dict.items():
    if key != 'PART' and key != 'PR' and key != 'SPRO':
        candidates_pos[key] = [x for x in set(val) if len(x) > 1]
    else:
        candidates_pos[key] = set(val)

print('Checking (un-)changeable properties.')
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


"""Разбиваем существительные также по одушевлённости (од/неод) и роду (муж/жен/cред), используя Mystem.
   Это нужно для выбора слов не только по частями речи, но и по другим грамматическим характеристикам.
   Обрати внимание - здесь ключом является не одно значение, а два - одушевлённость и род.
   Можно представить этот как двумерный словарь-таблицу.
   Отдельно выделяем имена, фамилии, отчества и географические названия."""

print('Parsing nouns.')

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

"""Глаголы разбиваем аналогичным образом по виду и переходности."""
print('Parsing verbs.')
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

"""Разбиваем местоимения по роду, лицу, одушевлённости и числу (если они не указаны, ставим прочерк)."""
print('Parsing pronouns.')
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

"""Сейчас у нас в словаре хранятся множества слов, а не списки.
   Исправим (иначе некоторые функции в дальнейшем могут не сработать)."""

candidates_pos = {k: list(v) for k, v in candidates_pos.items()}

print('Saving files.')
pickle.dump(candidates_pos, open(DATA_PATH + 'candidates_pos.p', 'wb'))
pickle.dump(candidates_verbs_grammar, open(DATA_PATH + 'candidates_verbs_grammar.p', 'wb'))
pickle.dump(candidates_nouns_grammar, open(DATA_PATH + 'candidates_nouns_grammar.p', 'wb'))
pickle.dump(candidates_pronouns_grammar, open(DATA_PATH + 'candidates_pronouns_grammar.p', 'wb'))
pickle.dump(named_entites, open(DATA_PATH + 'named_entites.p', 'wb'))