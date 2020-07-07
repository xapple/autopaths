#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair.
MIT Licensed.
Contact at www.sinclair.bio
"""

# Built-in modules #
import os, stat

################################################################################
class FilePermissions(object):
    """Container for reading and setting a files permissions."""

    def __init__(self, path):
        self.path = path

    @property
    def number(self):
        """The permission bits as an octal integer."""
        return os.stat(self.path).st_mode & 0o0777

    @property
    def is_executable(self):
        """Can you execute this file?"""
        return os.access(self.path, os.X_OK)

    def make_executable(self):
        return os.chmod(self.path, os.stat(self.path).st_mode | stat.S_IEXEC)

    def only_readable(self):
        """Remove all writing privileges."""
        return os.chmod(self.path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
