def reverse():
    print('reverse')
    from . import echo
    from .. import formats
    from ..filters import equalizer
    print('succesfully imported intra-package references')

if __name__ == "__main__":
    print('reverse main')