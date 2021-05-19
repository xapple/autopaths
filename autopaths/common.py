#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair.
MIT Licensed.
Contact at www.sinclair.bio
"""

# Built-in modules #
import re

###############################################################################
def natural_sort(item):
    """
    Sort strings that contain numbers correctly.

    >>> l = ['v1.3.12', 'v1.3.3', 'v1.2.5', 'v1.2.15', 'v1.2.3', 'v1.2.1']
    >>> l.sort(key=natural_sort)
    >>> l.__repr__()
    "['v1.2.1', 'v1.2.3', 'v1.2.5', 'v1.2.15', 'v1.3.3', 'v1.3.12']"
    """
    dre = re.compile(r'(\d+)')
    return [int(s) if s.isdigit() else s.lower() for s in re.split(dre, item)]

################################################################################
def pad_extra_whitespace(string, pad):
    """
    Given a multiline string, add extra whitespaces to the front of every line.
    """
    return '\n'.join(' ' * pad + line for line in string.split('\n'))
