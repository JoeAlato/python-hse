from collections import Iterable


def chain(*iterables):
    """
    >>> list(chain([[["test"]]]))
    ['t', 'e', 's', 't']
    """
    for iterable in iterables:
        if not isinstance(iterable, Iterable):
            yield iterable
        else:
            for item in iterable:
                if item != iterable:
                    yield from chain(item)
                else:
                    yield item