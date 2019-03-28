# Built-in modules #
import os, glob

# Internal modules #
import autopaths

# Constants #
if os.name == "posix": sep = "/"
if os.name == "nt":    sep = "\\"

################################################################################
class BasePath(str):
    """This object contains methods that are common to both FilePath objects
    and DirectoryPath objects."""

    def __repr__(self): return '<%s object "%s">' % (self.__class__.__name__, self.path)

    @classmethod
    def clean_path(cls, path):
        """Given a path, return a cleaned up version for initialization."""
        # Conserve 'None' object style #
        if path is None: return None
        # Don't nest BasePaths object or the like #
        if hasattr(path, 'path'): path = path.path
        # Expand the tilda #
        if "~" in path: path = os.path.expanduser(path)
        # We will store the path with the OS specific separator #
        # We will never mix both kinds of separators #
        if os.name == "posix": path = path.replace("\\", sep)
        if os.name == "nt":    path = path.replace("/",  sep)
        # Expand star #
        if "*" in path:
            matches = glob.glob(path)
            if len(matches) < 1: raise Exception("Found exactly no paths matching '%s'" % path)
            if len(matches) > 1: raise Exception("Found several paths matching '%s'" % path)
            path = matches[0]
        # Our standard is to end with a slash for directories #
        if cls is autopaths.dir_path.DirectoryPath:
            if not path.endswith(sep):
                path += sep
        # Return the result #
        return path

    def __new__(cls, path, *args, **kwargs):
        """A Path object is in fact a string"""
        return str.__new__(cls, cls.clean_path(path))

    def __init__(self, path):
        self.path = self.clean_path(path)

    def __add__(self, other):
        if os.name == "posix": other = other.replace("\\", sep)
        if os.name == "nt":    other = other.replace("/",  sep)
        if other.endswith(sep): return autopaths.dir_path.DirectoryPath(self.path + other)
        else:                   return autopaths.file_path.FilePath(self.path + other)

    # ------------------------------ Properties ----------------------------- #
    @property
    def escaped(self):
        """The path with special characters escaped.
        For instance a backslash becomes a double backslash."""
        return self.path.replace("\\", "\\\\")

    @property
    def unix_style(self):
        """The path with forward slashes and no disk drive."""
        if self.path[1] == ':': path = self.path[2:]
        else:                   path = self.path
        return path.replace("\\", "/")

    @property
    def wsl_style(self):
        """The path with forward slashes and a windows subsytem
        for linux style leading disk drive."""
        return "/mnt/c" + self.unix_style

    @property
    def win_style(self):
        """The path with backward slashes."""
        return self.path.replace("/", "\\")

    @property
    def exists(self):
        """Does it exist in the file system?
        Returns True even for broken symbolic links."""
        return os.path.lexists(self.path)

    @property
    def is_symlink(self):
        """Is this file a symbolic link to an other file?"""
        if os.name == "posix": return os.path.islink(self.path)
        if os.name == "nt":
            import win32api
            import win32con
            num = win32con.FILE_ATTRIBUTE_REPARSE_POINT
            return bool(win32api.GetFileAttributes(self.path) & num)

    @property
    def permissions(self):
        """Convenience object for dealing with permissions."""
        return autopaths.file_permissions.FilePermissions(self.path)

    @property
    def mdate(self):
        """Return the modification date as a unix time."""
        return os.path.getmtime(self.path)

    @property
    def mdate_iso(self):
        """Return the modification date as a datetime iso object."""
        return datetime.fromtimestamp(self.mdate).isoformat()

    @property
    def cdate(self):
        """Return the creation date."""
        return os.path.getctime(self.path)

    @property
    def cdate_iso(self):
        """Return the creation date as a datetime iso object."""
        return datetime.fromtimestamp(self.cdate).isoformat()
