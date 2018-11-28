#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from numbers import Number
from typing import List


def regexp_0(text: str, pattern: str) -> List[slice]:
    """
    Finds the occurrence and position of the substrings within a string
    >>> regexp_0("LingvoX SpaceX SpacoX", "oX")
    [slice(5, 7, None), slice(19, 21, None)]
    """
    return [slice(x.start(), x.end(), None)
            for x in re.finditer(pattern, text)]


"""
https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
"""


def regexp_1(text: str) -> str:
    """
    Converts camel case string to snake case string
    >>> regexp_1("QObject")
    'q_object'
    >>> regexp_1("KNeighborsClassifier")
    'k_neighbors_classifier'
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    result = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return result


def regexp_2(text: str, length: int) -> str:
    """
    Removes words from a string of length between 1 and a given number
    >>> regexp_2("Hello Cyril Kak dela bro", 3)
    'Hello Cyril dela'
    >>> regexp_2("Hello Cyril Kak dela bro", 4)
    'Hello Cyril'
    """
    my_regex = r"\b\w{1," + re.escape(str(length)) + r"}\b"
    result = re.sub(my_regex, '', text)
    result = re.sub(r'\s{2,}', ' ', result).strip()
    return result


def regexp_3(text: str) -> str:
    """
    Removes the parenthesis area in a string
    >>> regexp_3("Mark (Station) (LingvoX)")
    'Mark'
    """
    result = re.sub(r'\((.?)*\)', '', text).strip()
    return result


def regexp_3(text: str) -> str:
    """
    Removes the parenthesis area in a string
    >>> regexp_3("Polina (Ivan)")
    'Polina'

    >>> regexp_3("Mark (Station) (LingvoX)")
    'Mark'
    """
    result = re.sub(r'\((.?)*\)', '', text).strip()
    return result


def regexp_4(num: Number) -> bool:
    """
    Returns true whenever a decimal with a precision of 2
    >>> regexp_4(1.22)
    True
    >>> regexp_4(1.2)
    True
    >>> regexp_4(11)
    True
    >>> regexp_4(11.)
    True
    >>> regexp_4(11.333)
    False
    """
    my_regex = re.compile(r"^\d+(\.\d{0,2})?$")
    text = str(num)
    result = re.match(my_regex, text)
    if result:
        return True
    return False


if __name__ == "__main__":
    import doctest
    doctest.testmod()
