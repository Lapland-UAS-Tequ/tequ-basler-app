import sys


def ePrint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

