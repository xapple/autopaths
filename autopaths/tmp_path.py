# Built-in modules #
import tempfile

# Internal modules #
from autopaths.file_path import FilePath
from autopaths.dir_path  import DirectoryPath

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
    handle = tempfile.NamedTemporaryFile(delete=False, **kwargs)
    path   = handle.name
    handle.close()
    return FilePath(path)

################################################################################
def new_temp_dir(**kwargs):
    return DirectoryPath(tempfile.mkdtemp(**kwargs) + '/')
