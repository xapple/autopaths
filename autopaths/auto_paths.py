#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair.
MIT Licensed.
Contact at www.sinclair.bio
"""

# Built-in modules #
import os, tempfile, re

# Internal modules #
import autopaths

# Constants #
if os.name == "posix": sep = "/"
if os.name == "nt":    sep = "\\"

# Delimiters #
delimiters = ('_', '.', '/')
pattern = re.compile('|'.join(map(re.escape, delimiters)))

###############################################################################
class AutoPaths:
    """
    You can use this class like this when making pipelines:

        class Sample(object):

            all_paths = '''
                        /raw/raw.sff
                        /raw/raw.fastq
                        /clean/trim.fastq
                        /clean/clean.fastq   # Use this file for run step
                        '''

            def __init__(self, base_dir):
                self.p = AutoPaths(base_dir, self.all_paths)

            def clean(self):
                shutil.move(self.p.raw_sff, self.p.clean_fastq)
    """

    def __repr__(self):
        return '<%s object on "%s">' % (self.__class__.__name__,
                                        self._base_dir)

    def __init__(self, base_dir, all_paths):
        # Don't nest Path objects or the like #
        if hasattr(base_dir, 'path'): base_dir = base_dir.path
        # Attributes #
        self._base_dir  = os.path.expanduser(base_dir)
        self._all_paths = all_paths
        self._tmp_dir   = tempfile.gettempdir() + sep
        # Parse input #
        self._paths = [p for p in all_paths.split('\n') if p.strip(' ')]
        self._paths = [PathItems(p.strip(' '), base_dir) for p in self._paths]

    def __call__(self, key):    return self.__getattr__(key)
    def __getitem__(self, key): return self.__getattr__(key)
    def get(self, key):         return self.__getattr__(key)

    def __getattr__(self, key):
        # Let built-ins pass through to object #
        if key.startswith('__') and key.endswith('__'):
            return object.__getattr__(key)
        # Special cases that should go to the actual dictionary #
        if key.startswith('_'): return self.__dict__[key]
        # Temporary items #
        if key == 'tmp_dir': return self.__dict__['_tmp_dir']
        if key == 'tmp':     return self.__dict__['tmp']
        # Search #
        items = pattern.split(key)
        # Is it a directory ? #
        if items[-1] == 'dir':
            items.pop(-1)
            return self.search_for_dir(key, items)
        else:
            return self.search_for_file(key, items)

    def __iter__(self):
        """Yield all the paths we have stored."""
        for path in self._paths: yield autopaths.Path(path.complete_path)

    def search_for_file(self, key, items):
        # Search #
        matches = [set([p for p in self._paths if i in p]) for i in items]
        result = set.intersection(*matches)
        # No matches #
        if len(result) == 0:
            raise Exception("Could not find any path matching '%s'" % key)
        # Multiple matches, advantage file name #
        if len(result) > 1:
            best_score = max([p.score_file(items) for p in result])
            result = [p for p in result if p.score_file(items) >= best_score]
        # Multiple matches, take the one with less parts #
        if len(result) > 1:
            shortest = min([len(p) for p in result])
            result = [p for p in result if len(p) <= shortest]
        # Multiple matches, error #
        if len(result) > 1:
            raise Exception("Found several paths matching '%s'" % key)
        # Make the directory #
        result = result.pop()
        directory = autopaths.dir_path.DirectoryPath(result.complete_dir)
        if not directory.exists: directory.create(safe=True)
        # Return base case #
        return autopaths.file_path.FilePath(result.complete_path)

    def search_for_dir(self, key, items):
        # Search #
        matches = [set([p for p in self._paths if i in p]) for i in items]
        result = set.intersection(*matches)
        # No matches #
        if len(result) == 0:
            raise Exception("Could not find any path matching '%s'" % key)
        # Multiple matches, advantage dir name #
        if len(result) > 1:
            best_score = max([p.score_dir(items) for p in result])
            result = [p for p in result if p.score_dir(items) >= best_score]
        # Multiple matches, take the one with less parts #
        if len(result) > 1:
            shortest = min([len(p) for p in result])
            result = [p for p in result if len(p) <= shortest]
        # Multiple matches, maybe they all are the same directory #
        if len(result) > 1:
            if len(set([p.dir for p in result])) == 1: result = [result[0]]
        # Multiple matches, error #
        if len(result) > 1:
            raise Exception("Found several paths matching '%s'" % key)
        # Make the directory #
        result = result.pop()
        directory = autopaths.dir_path.DirectoryPath(result.complete_dir)
        if not directory.exists: directory.create(safe=True)
        # Return #
        return directory

    @property
    def tmp_dir(self):
        if not self._tmp_dir: self._tmp_dir = tempfile.mkdtemp() + sep
        return self._tmp_dir

    @property
    def tmp(self):
        return self.tmp_dir + 'autopath.tmp'

###############################################################################
class PathItems:

    def __repr__(self):
        return '<%s object "%s">' % (self.__class__.__name__, self.path)

    def __init__(self, path, base_dir):
        # The parameters passed #
        self.path     = path
        self.base_dir = base_dir
        # Remove any comments #
        if '#' in self.path: self.path = self.path[:self.path.index('#')]
        # Split the file name and the directory #
        self.dir, self.name = os.path.split(path)
        # Split every item based on our separators #
        self.name_items = pattern.split(self.name) if self.name else []
        self.dir_items  = pattern.split(self.dir)  if self.dir  else []
        # Combine items from name and directory #
        self.all_items  = self.name_items + self.dir_items

    def __contains__(self, i):
        return i in self.all_items

    def __len__(self):
        return len(self.all_items)

    def score_file(self, items):
        return sum([1.0 if i in self.name_items else 0.5
                    for i in items if i in self])

    def score_dir(self, items):
        return sum([1.0 if i in self.dir_items else 0.5
                    for i in items if i in self])

    @property
    def complete_path(self):
        return os.path.abspath(self.base_dir + self.path)

    @property
    def complete_dir(self):
        return os.path.abspath(self.base_dir + self.dir) + sep

    @property
    def path_obj(self):
        return autopaths.Path(self.complete_path)
