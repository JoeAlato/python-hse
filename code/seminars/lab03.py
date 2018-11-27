def zip_(*iterables):
    """
    The same as built-in zip(), but generator
    >>> for i, j, k in zip_(range(3), range(4), range(-7, 0)):
    ...     print(i, j, k)
    0 0 -7
    1 1 -6
    2 2 -5
    """
    sentinel = object()
    iterators = [iter(it) for it in iterables]
    print('iterators:', iterators)
    while iterators:
        result = []
        for it in iterators:
            elem = next(it, sentinel)
            if elem is sentinel:
                print('return')
                return
            result.append(elem)
            print('result:', result)
        yield tuple(result)

for i, j, k in zip_(range(3), range(4), range(-7, 0)):
    print(i, j, k)