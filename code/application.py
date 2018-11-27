from flask import Flask, request, url_for
from flask import render_template
app = Flask(__name__)
import re
import operator
import random
from collections import Counter
import urllib.request
from bs4 import BeautifulSoup
from alphabet_detector import AlphabetDetector
ad = AlphabetDetector()
with urllib.request.urlopen('https://yandex.ru/pogoda/10463?') as response:
    html = response.read()
soup = BeautifulSoup(html, 'html.parser')
old_dictionary = {"бледный": "блѣдный", "гнедой": "гнѣдой",
                  "змей": "змѣй", "лелеять": "лелѣять", "недра": "нѣдра",
                  "певец": "пѣвецъ", "свирель": "свирѣль", "слепой": "слѣпой",
                  "зрение": "зрѣніе", "ездить": "ѣздить"}


def prerevolutionary_form(word):
    if word in old_dictionary.keys():
        return old_dictionary[word]
    else:
        result = word + "ъ"
        return result


def scrape_weather():
    temp = -100
    for elem in soup.find("div", {"class": "fact__temp"}):
        if elem['class'][0] == "temp__value":
            temp = elem.text
    try:
        wind_speed = soup.find("span", {"class": "wind-speed"}).text
    except:
        wind_speed = 0
    condition = soup.find("div", {"class": "fact__condition"}).text
    return temp, wind_speed, condition


def get_condition_image(condition_text):
    condition_text = condition_text.lower()
    if 'ясно' in condition_text:
        return "fa-sun-o"
    elif 'снег' in condition_text:
        return "fa-snowflake-o"
    elif 'дождь' in condition_text:
        return "fa-tint"
    else:
        return "fa-cloud"


temp, wind_speed, condition = scrape_weather()
condition_image = get_condition_image(condition)


def validate_query(query):
    if len(query) == 0:
        return False, "Вы ввели пустое слово, попробуйте ещё раз."
    else:
        return True, ""


@app.route('/', methods=['GET', 'POST'])
def index():
    error = ""
    result = ""
    word = ""
    if request.method == "POST":
        print(request.method)
        try:
            word = request.form['received_word']
            print("Received word: ", word)
            valid, error = validate_query(word)
            if valid:
                result = prerevolutionary_form(word)
                print("Result: ", result)
            else:
                print(error)
        except Exception as e:
            error = e
            print("Error: ", e)
    return render_template('index.html', error=error, result=result, word=word,
                           temp=temp, wind_speed=wind_speed, condition=condition_image)


def validate_word(word):
    regex_cyr_word = re.compile("[А-я]+(?:-[А-я]*)*")
    if regex_cyr_word.match(word):
        if ad.is_cyrillic(word):
            return True
    return False


def preprocess_text(text):
    result = re.sub('([.,!?()»«])', r' \1 ', text)
    result = re.sub('\s{2,}', ' ', result)
    return result


@app.route('/vpravda', methods=['GET', 'POST'])
def newspaper():
    error = ""
    req_newspaper = urllib.request.Request('http://vpravda.ru/')
    html_newspaper = urllib.request.urlopen(req_newspaper).read()
    soup_newspaper = BeautifulSoup(html_newspaper, 'html.parser')
    text = soup_newspaper.text.split("\n")
    text = [x for x in text if x != '']
    words = [word for line in text for word in preprocess_text(line).split() if validate_word(word)]
    unique_words = set(words)
    prerevolutionary_words = [prerevolutionary_form(word) for word in unique_words]
    words_freq = Counter(words)
    most_frequent_words = [elem[0] for elem in words_freq.most_common(10)]
    return render_template('vpravda.html', error=error, most_frequent_words=most_frequent_words, prerevolutionary_words=prerevolutionary_words,
                           temp=temp, wind_speed=wind_speed, condition=condition_image)

quiz_questions = []
words = list(old_dictionary.keys())[:10]
for word in words:
    first_correct = random.choice([True, False])
    if first_correct:
        quiz_questions.append([prerevolutionary_form(word), word, 0])
    else:
        quiz_questions.append([word, prerevolutionary_form(word), 1])

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    global quiz_questions
    if request.method == 'POST':
        error = ""
        correct_choices = [-1] * len(quiz_questions)
        checked = [-1] * len(quiz_questions)
        for i, question in enumerate(quiz_questions):
            if request.form.get("question_" + str(i) + "_option_" + str(question[2])):
                if request.form.get("question_" + str(i) + "_option_" + str(int(not(bool(question[2]))))):
                    correct_choices[i] = False
                else:
                    correct_choices[i] = True
            else:
                correct_choices[i] = False
            if request.form.get("question_" + str(i) + "_option_0"):
                checked[i] = True
            else:
                if request.form.get("question_" + str(i) + "_option_1"):
                    checked[i] = False
        return render_template('quiz.html', error=error, quiz_questions=quiz_questions,
                               correct_choices = correct_choices, checked=checked,
                               temp=temp, wind_speed=wind_speed, condition=condition_image)
    else:
        error = ""
        correct_choices = [-1] * len(quiz_questions)
        checked = [-1] * len(quiz_questions)
        return render_template('quiz.html', error=error, quiz_questions=quiz_questions,
                               correct_choices = correct_choices, checked=checked,
                               temp=temp, wind_speed=wind_speed, condition=condition_image)


if __name__ == '__main__':
    app.run(debug=True)
