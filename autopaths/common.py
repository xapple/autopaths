# Built-in modules #
import os, hashlib, re

###############################################################################
def natural_sort(item):
    """
    Sort strings that contain numbers correctly. Works in Python 2 and 3.

    >>> l = ['v1.3.12', 'v1.3.3', 'v1.2.5', 'v1.2.15', 'v1.2.3', 'v1.2.1']
    >>> l.sort(key=natural_sort)
    >>> l.__repr__()
    "['v1.2.1', 'v1.2.3', 'v1.2.5', 'v1.2.15', 'v1.3.3', 'v1.3.12']"
    """
    dre = re.compile(r'(\d+)')
    return [int(s) if s.isdigit() else s.lower() for s in re.split(dre, item)]