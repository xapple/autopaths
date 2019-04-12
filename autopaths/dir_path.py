# Built-in modules #
import os, shutil, glob

# Internal modules #
import autopaths

# Constants #
if os.name == "posix": sep = "/"
if os.name == "nt":    sep = "\\"

################################################################################
class DirectoryPath(autopaths.base_path.BasePath):
    """Represents a string to a directory path and adds methods to interact with
    directories."""

    def __iter__(self): return self.flat_contents

    def __contains__(self, item): return item in [x.name for x in self.flat_contents]

    def __getitem__(self, item):
        for path in self.flat_contents:
            if path.name == item:
                return path
        raise KeyError("Couldn't find '%s' in '%s'" % (item, self.path))

    # ------------------------------ Properties ----------------------------- #
    @property
    def p(self):
        if not hasattr(self, 'all_paths'):
            raise Exception("You need to define 'all_paths' to use this function")
        return autopaths.auto_paths.AutoPaths(self.path, self.all_paths)

    @property
    def name(self):
        """Just the directory name."""
        return os.path.basename(os.path.dirname(self.path))

    @property
    def prefix_path(self):
        """The full path without the extension."""
        return os.path.splitext(self.path)[0].rstrip(sep)

    @property
    def absolute_path(self):
        """The absolute path starting with a `/`."""
        return os.path.abspath(self.path) + sep

    @property
    def directory(self):
        """The full path of the directory containing this one."""
        # The built-in function #
        directory = os.path.dirname(os.path.dirname(self.path))
        # Maybe we need to go the absolute path way #
        if not directory:
            directory = os.path.dirname(os.path.dirname(self.absolute_path))
        # Return #
        return autopaths.dir_path.DirectoryPath(directory)

    @property
    def empty(self):
        """Does the directory contain no files?"""
        return len(list(self.flat_contents)) == 0

    @property
    def size(self):
        """The total size in bytes of all file contents."""
        return autopaths.file_size.FileSize(sum(f.count_bytes for f in self.files))

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
        else:
            result = []
        result.sort(key=lambda x: autopaths.common.natural_sort(x.path))
        return result

    @property
    def flat_directories(self):
        """The directories in this directory non-recursively, and sorted."""
        for root, dirs, files in os.walk(self.path):
            result = [DirectoryPath(os.path.join(root, d)) for d in dirs]
            break
        else:
            result = []
        result.sort(key=lambda x: autopaths.common.natural_sort(x.path))
        return result

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
        os.remove(self.path.rstrip(sep))
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

    def move_to(self, path):
        """Move the directory."""
        # Check #
        assert not os.path.exists(path)
        shutil.move(self.path, path)
        # Update the internal link #
        self.path = path

    def zip(self, keep_orig=False):
        """Make a zip archive of the directory"""
        shutil.make_archive(self.prefix_path , "zip", self.directory, self.name)
        if not keep_orig: self.remove()

    def copy(self, path):
        assert not os.path.exists(path)
        shutil.copytree(str(self.path), str(path))

    def glob(self, pattern):
        """Perform a glob search in this directory."""
        files = glob.glob(self.path + pattern)
        return map(autopaths.file_path.FilePath, files)

    def find(self, pattern):
        """Find a file in this directory."""
        f = glob.glob(self.path + pattern)[0]
        return autopaths.file_path.FilePath(f)