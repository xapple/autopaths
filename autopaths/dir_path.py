# Built-in modules #
import os, shutil
import glob, warnings

# Internal modules #
import autopaths

################################################################################
class DirectoryPath(str):

    def __repr__(self): return '<%s object "%s">' % (self.__class__.__name__, self.path)

    @classmethod
    def clean_path(cls, path):
        """Given a path, return a cleaned up version for initialization."""
        # Conserve 'None' object style #
        if path is None: return None
        # Don't nest DirectoryPaths or the like #
        if hasattr(path, 'path'): path = path.path
        # Expand the tilda #
        if "~" in path: path = os.path.expanduser(path)
        # Our standard is to end with a slash for directories #
        if not path.endswith('/'): path += '/'
        # Return the result #
        return path

    def __new__(cls, path, *args, **kwargs):
        """A DirectoryPath is in fact a string"""
        return str.__new__(cls, cls.clean_path(path))

    def __init__(self, path):
        self.path = self.clean_path(path)

    def __add__(self, other):
        if other.endswith("/"): return DirectoryPath(self.path + other)
        else:                   return autopaths.file_path.FilePath(self.path + other)

    def __iter__(self): return self.flat_contents

    @property
    def p(self):
        if not hasattr(self, 'all_paths'):
            raise Exception("You need to define 'all_paths' to use this function")
        return autopaths.auto_paths.AutoPaths(self.path, self.all_paths)

    @property
    def name(self):
        """Just the directory name"""
        return os.path.basename(os.path.dirname(self.path))

    @property
    def prefix_path(self):
        """The full path without the extension"""
        return os.path.splitext(self.path)[0].rstrip('/')

    @property
    def absolute_path(self):
        """The absolute path starting with a `/`"""
        return os.path.abspath(self.path) + '/'

    @property
    def directory(self):
        """The full path of the directory containing this one."""
        return DirectoryPath(os.path.dirname(os.path.dirname(self.path)))

    #-------------------------- Recursive contents ---------------------------#
    @property
    def contents(self):
        """The files and directories in this directory, recursively."""
        for root, dirs, files in os.walk(self.path, topdown=False):
            for d in dirs:  yield DirectoryPath(os.path.join(root, d))
            for f in files: yield autopaths.file_path.FilePath(os.path.join(root, f))

    @property
    def files(self):
        """The files in this directory, recursively."""
        for root, dirs, files in os.walk(self.path, topdown=False):
            for f in files: yield autopaths.file_path.FilePath(os.path.join(root, f))

    @property
    def directories(self):
        """The directories in this directory, recursively."""
        for root, dirs, files in os.walk(self.path, topdown=False):
            for d in dirs: yield DirectoryPath(os.path.join(root, d))

    #----------------------------- Flat contents -----------------------------#
    @property
    def flat_contents(self):
        """The files and directories in this directory non-recursively."""
        for root, dirs, files in os.walk(self.path):
            for d in dirs:  yield DirectoryPath(os.path.join(root, d))
            for f in files: yield autopaths.file_path.FilePath(os.path.join(root, f))
            break

    @property
    def flat_files(self):
        """The files in this directory non-recursively, and sorted.
        #TODO: check for permission denied in directory."""
        for root, dirs, files in os.walk(self.path):
            result = [autopaths.file_path.FilePath(os.path.join(root, f)) for f in files]
            break
        result.sort(key=lambda x: autopaths.common.natural_sort(x.path))
        return result

    @property
    def flat_directories(self):
        """The directories in this directory non-recursively, and sorted."""
        for root, dirs, files in os.walk(self.path):
            result = [DirectoryPath(os.path.join(root, d)) for d in dirs]
            break
        result.sort(key=lambda x: autopaths.common.natural_sort(x.path))
        return result

    #-------------------------------- Other ----------------------------------#
    @property
    def is_symlink(self):
        """Is this directory a symbolic link to an other directory?"""
        return os.path.islink(self.path.rstrip('/'))

    @property
    def exists(self):
        """Does it exist in the file system?"""
        return os.path.lexists(self.path) # Include broken symlinks

    @property
    def empty(self):
        """Does the directory contain no files?"""
        return len(list(self.flat_contents)) == 0

    @property
    def permissions(self):
        """Convenience object for dealing with permissions."""
        return autopaths.file_permissions.FilePermissions(self.path)

    @property
    def mod_time(self):
        """The modification time"""
        return os.stat(self.path).st_mtime

    @property
    def size(self):
        """The total size in bytes of all file contents."""
        return autopaths.file_path.FileSize(sum(f.count_bytes for f in self.files))

    #------------------------------- Methods ---------------------------------#
    def must_exist(self):
        """Raise an exception if the directory doesn't exist."""
        if not os.path.isdir(self.path):
            raise Exception("The directory path '%s' does not exist." % self.path)

    def remove(self):
        if not self.exists: return False
        if self.is_symlink: return self.remove_when_symlink()
        shutil.rmtree(self.path, ignore_errors=True)
        return True

    def remove_when_symlink(self):
        if not self.exists: return False
        os.remove(self.path.rstrip('/'))
        return True

    def create(self, safe=False, inherit=True):
        # Create it #
        if not safe:
            os.makedirs(self.path)
            if inherit: os.chmod(self.path, self.directory.permissions.number)
        if safe:
            try:
                os.makedirs(self.path)
                if inherit: os.chmod(self.path, self.directory.permissions.number)
            except OSError: pass

    def create_if_not_exists(self):
        if not self.exists: self.create()

    def zip(self, keep_orig=False):
        """Make a zip archive of the directory"""
        shutil.make_archive(self.prefix_path , "zip", self.directory, self.name)
        if not keep_orig: self.remove()

    def link_from(self, where, safe=False):
        """Make a link here pointing to another directory somewhere else.
        The destination is hence self.path and the source is *where*"""
        if not safe:
            self.remove()
            return os.symlink(where, self.path.rstrip('/'))
        if safe:
            try: self.remove()
            except OSError: pass
            try: os.symlink(where, self.path.rstrip('/'))
            except OSError: warnings.warn("Symlink of %s to %s did not work" % (where, self))

    def copy(self, path):
        assert not os.path.exists(path)
        shutil.copytree(self.path, path)

    def glob(self, pattern):
        """Perform a glob search in this directory."""
        files = glob.glob(self.path + pattern)
        return map(autopaths.file_path.FilePath, files)

    def find(self, pattern):
        """Find a file in this directory."""
        f = glob.glob(self.path + pattern)[0]
        return autopaths.file_path.FilePath(f)