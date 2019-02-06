# Built-in modules #
import os, inspect

# Get current directory (works always) #
file_name = os.path.abspath((inspect.stack()[0])[1])
this_dir  = os.path.dirname(os.path.abspath(file_name)) + '/'

# Internal modules #
from autopaths.dir_path import DirectoryPath

###############################################################################
def test_list_files():
    d = DirectoryPath(this_dir)
    list(d.files)