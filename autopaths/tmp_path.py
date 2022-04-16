#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair.
MIT Licensed.
Contact at www.sinclair.bio
"""

# Built-in modules #
import tempfile

################################################################################
def new_temp_handle(**kwargs):
    """A new temporary handle ready to be written to."""
    handle = tempfile.NamedTemporaryFile(delete=False, **kwargs)
    return handle

################################################################################
def new_temp_path(**kwargs):
    """A new temporary path."""
    handle = tempfile.NamedTemporaryFile(**kwargs)
    path   = handle.name
    handle.close()
    return path

################################################################################
def new_temp_file(**kwargs):
    """A new temporary path as a FilePath object."""
    # Don't delete the file #
    kwargs['delete'] = False
    # Make an empty file and keep it #
    path = new_temp_path(**kwargs)
    # Make it into a FilePath object #
    from autopaths.file_path import FilePath
    return FilePath(path)

################################################################################
def new_temp_dir(**kwargs):
    # Create an empty directory #
    directory = tempfile.mkdtemp(**kwargs) + '/'
    # Make it into a DirectoryPath object #
    from autopaths.dir_path import DirectoryPath
    return DirectoryPath(directory)
