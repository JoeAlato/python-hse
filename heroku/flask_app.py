# A very simple Flask Hello World app for you to get started with...
# -*- coding: utf-8 -*-
from pymystem3 import Mystem
from pymorphy2 import MorphAnalyzer
from flask import Flask
from flask import render_template
from flask import request
import random
import pandas as pd
import pickle
import nltk
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
nltk.download('punkt')
sns.set_style("whitegrid")
from nltk.probability import FreqDist
app = Flask(__name__)

morph = MorphAnalyzer()
m = Mystem()

DATA_PATH = "/home/kaprushka/mysite/data/"
candidates_pos = pickle.load(open(DATA_PATH + 'candidates_pos.p', 'rb'))
candidates_verbs_grammar = pickle.load(open(DATA_PATH + 'candidates_verbs_grammar.p', 'rb'))
candidates_nouns_grammar = pickle.load(open(DATA_PATH + 'candidates_nouns_grammar.p', 'rb'))
candidates_pronouns_grammar = pickle.load(open(DATA_PATH + 'candidates_pronouns_grammar.p', 'rb'))
named_entites = pickle.load(open(DATA_PATH + 'named_entites.p', 'rb'))
named_entities_labels = ['гео', 'имя', 'фам', 'отч']

def parse_verb_analysis(an):
    if 'analysis' in an.keys():
        tags = an['analysis'][0]['gr']
        non_changeable, changeable = tags.split('=')
        if '|' in changeable:
            changeable = changeable.split("|")[0]
        tags = non_changeable.split(',') + changeable.split(',')
        perf_tag, trans_tag = '-', '-'
        for tag in tags:
            if tag in ['несов', 'сов']:
                perf_tag = tag
            if tag in ['пе', 'нп']:
                trans_tag = tag
    return tags, perf_tag, trans_tag

def parse_pronoun_analysis(an):
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

def parse_noun_analysis(an):
    if 'analysis' in an.keys():
        non_changeable, changeable = an['analysis'][0]['gr'].split('=')
        tags = non_changeable.split(',')
        if '|' in changeable:
            changeable = changeable.split("|")[0]
        gender_tag = tags[1]
        if len(tags) > 2:
            anim_tag = tags[2]
        else:
            anim_tag = '-'
    return tags, gender_tag, anim_tag

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

"""Наконец, пишем полную функцию, которая принимает на вход текст, разбивает его на слова и анализирует с помощью Mystem,
   затем выбирает случайное слово нужной части речи и с нужными характеристиками и, наконец,
   копирует изменяемые грамматические признаки из слов оригинала в слова нашего сгенерированного предложения."""

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
                tags, gender_tag, anim_tag = parse_noun_analysis(an)
                for label in named_entities_labels:
                    if label in tags:
                        possible_values = named_entites[label]
                        is_ne = True
                if not is_ne:
                    possible_values = candidates_nouns_grammar[(gender_tag, anim_tag)]
            elif pos_tag == 'V':
                tags, perf_tag, trans_tag = parse_verb_analysis(an)
                print(tags)
                possible_values = candidates_verbs_grammar[(perf_tag, trans_tag)]
            elif pos_tag == 'SPRO':
                tags, person_tag, num_tag, gender_tag, anim_tag = parse_pronoun_analysis(an)
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


@app.route('/')
def main():
    return render_template('index.html', statement = 'Введите ваш текст')

@app.route('/', methods=['POST'])
def main_post():
    text = request.form['text']
    statement = generate_response(text)
    return render_template('index.html', statement = statement)


@app.route('/iz', methods = ['GET', 'POST'])
def plot_iz():
    pd_data = pd.read_csv('data/iz.csv')
    tokens = pd_data['text'].apply(str.lower).apply(nltk.tokenize.word_tokenize)
    all_tokens = [token for text in tokens for token in text]
    fd = FreqDist(all_tokens)
    data = {x[0]: x[1] for x in fd.most_common(10)}
    plt.xticks(rotation='vertical')
    plt.bar(data.keys(), data.values(), 1, edgecolor = 'w', color='g')
    ax = sns.barplot(list(data.keys()), list(data.values()))
    plt.savefig('plot.png')
    return render_template('iz.html')
