# Built-in modules #
import os, tempfile, subprocess, shutil, codecs, gzip
import glob, zipfile, datetime, re, codecs

# Internal modules #
import autopaths

# Third party modules #
if os.name == "posix": import sh
if os.name == "nt":    import pbs

# Constants #
if os.name == "posix": sep = "/"
if os.name == "nt":    sep = "\\"

################################################################################
class FilePath(str):
    """I can never remember all those darn `os.path` commands, so I made a class
    that wraps them with an easier and more pythonic syntax.

        path = FilePath('/home/root/text.txt')
        print path.extension
        print path.directory
        print path.filename

    You can find lots of the common things you would need to do with file paths.
    Such as: path.make_executable() etc etc."""

    def __repr__(self):    return '<%s object "%s">' % (self.__class__.__name__, self.path)

    def __nonzero__(self): return self.path != None and self.count_bytes != 0

    def __list__(self):    return self.count

    def __iter__(self):
        # Maybe no not overwrite iter() #
        with open(self.path, 'r') as handle:
            for line in handle: yield line

    def __len__(self):
        if self.path is None: return 0
        return self.count

    def __new__(cls, path, *args, **kwargs):
        """A FilePath is in fact a string."""
        return str.__new__(cls, cls.clean_path(path))

    def __init__(self, path):
        self.path = self.clean_path(path)

    def __add__(self, other):
        if os.name == "posix": other = other.replace("\\", sep)
        if os.name == "nt":    other = other.replace("/",  sep)
        if other.endswith(sep): return autopaths.dir_path.DirectoryPath(self.path + other)
        else:                   return FilePath(self.path + other)

    def __sub__(self, directory):
        """Subtract a directory from the current path to get the relative path
        of the current file from that directory."""
        return os.path.relpath(self.path, directory)

    def __enter__(self):
        """Called when entering the 'with' statement (context manager)."""
        return self

    def __exit__(self, errtype, value, traceback):
        """Called when exiting the 'with' statement.
        This enables us to close the file or database properly, even when
        exceptions are raised."""
        self.close()

    # ------------------------------ Class methods ----------------------------- #
    @classmethod
    def clean_path(cls, path):
        """Given a path, return a cleaned up version for initialization."""
        # Conserve None object style #
        if path is None: return None
        # Don't nest FilePaths or the like #
        if hasattr(path, 'path'): path = path.path
        # Expand tilda #
        if "~" in path: path = os.path.expanduser(path)
        # We will store the path with the OS specific separator #
        # We will never mix both kinds of separators #
        if os.name == "posix": path = path.replace("\\", sep)
        if os.name == "nt":    path = path.replace("/",  sep)
        # Expand star #
        if "*" in path:
            matches = glob.glob(path)
            if len(matches) < 1: raise Exception("Found exactly no files matching '%s'" % path)
            if len(matches) > 1: raise Exception("Found several files matching '%s'" % path)
            path = matches[0]
        # Return the result #
        return path

    # ------------------------------ Properties ----------------------------- #
    @property
    def first(self):
        """Just the first line. Don't try this on binary files."""
        with open(self.path, 'r') as handle:
            for line in handle: return line

    @property
    def exists(self):
        """Does it exist in the file system."""
        return os.path.lexists(self.path) # Returns True even for broken symbolic links

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
    def prefix_path(self):
        """The full path without the (last) extension and trailing period."""
        return str(os.path.splitext(self.path)[0])

    @property
    def prefix(self):
        """Just the filename without the (last) extension and trailing period."""
        return str(os.path.basename(self.prefix_path))

    @property
    def short_prefix(self):
        """Just the filename without any extension or periods."""
        return self.filename.split('.')[0]

    @property
    def name(self):
        """Shortcut for self.filename."""
        return self.filename

    @property
    def filename(self):
        """Just the filename with the extension."""
        return str(os.path.basename(self.path))

    @property
    def extension(self):
        """The extension with the leading period."""
        return os.path.splitext(self.path)[1]

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
    def directory(self):
        """The directory containing this file."""
        # The built-in function #
        directory = os.path.dirname(self.path)
        # Maybe we need to go the absolute path way #
        if not directory: directory = os.path.dirname(self.absolute_path)
        # Return #
        return autopaths.dir_path.DirectoryPath(directory)

    @property
    def count_bytes(self):
        """The number of bytes."""
        if not self.exists: return 0
        return os.path.getsize(self.path)

    @property
    def count(self):
        """We are going to default to the number of lines."""
        if os.name == "posix": return int(sh.wc('-l', self.path).split()[0])
        if os.name == "nt":    return int(pbs.Command("find")('/c', '/v', '""', self.path))

    @property
    def size(self):
        """Human readable file size."""
        return autopaths.file_size.FileSize(self.count_bytes)

    @property
    def permissions(self):
        """Convenience object for dealing with permissions."""
        return autopaths.file_permissions.FilePermissions(self.path)

    @property
    def contents(self):
        """The contents as a string."""
        with open(self.path, 'r') as handle: return handle.read()

    @property
    def contents_utf8(self):
        """The contents as a unicode string."""
        with codecs.open(self.path, encoding='utf8') as handle:return handle.read()

    @property
    def absolute_path(self):
        """The absolute path starting with a `/`."""
        return FilePath(os.path.abspath(self.path))

    @property
    def physical_path(self):
        """The physical path like in `pwd -P`."""
        return FilePath(os.path.realpath(self.path))

    @property
    def relative_path(self):
        """The relative path when compared with current directory."""
        return FilePath(os.path.relpath(self.physical_path))

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

    @property
    def md5(self):
        """Return the md5 checksum."""
        return autopaths.common.md5sum(self.path)

    @property
    def might_be_binary(self):
        """Try to quickly guess if the file is binary."""
        from binaryornot.check import is_binary
        return is_binary(self.path)

    @property
    def contains_binary(self):
        """Return True if the file contains binary characters."""
        from binaryornot.helpers import is_binary_string
        return is_binary_string(self.contents)

    #-------------------------------- Methods --------------------------------#
    def read(self, encoding=None):
        with codecs.open(self.path, 'r', encoding) as handle: content = handle.read()
        return content

    def create(self):
        if not self.directory.exists: self.directory.create()
        self.open('w')
        return self

    def touch(self):
        """Just create an empty file if it does not exist."""
        with open(self.path, 'a'): os.utime(self.path, None)

    def open(self, mode='r'):
        self.handle = open(self.path, mode)
        return self.handle

    def add_str(self, string):
        self.handle.write(string)

    def close(self):
        self.handle.close()

    def write(self, content, encoding=None, mode='w'):
        if encoding is None:
            with open(self.path, mode) as handle: handle.write(content)
        else:
            with codecs.open(self.path, mode, encoding) as handle: handle.write(content)

    def writelines(self, content, encoding=None):
        if encoding is None:
            with open(self.path, 'w') as handle: handle.writelines(content)
        else:
            with codecs.open(self.path, 'w', encoding) as handle: handle.writelines(content)

    def remove(self):
        if not self.exists: return False
        os.remove(self.path)
        return True

    def copy(self, path):
        """Copy to this path."""
        # Directory special case #
        if path.endswith(sep): path += self.filename
        # Normal case #
        shutil.copy2(self.path, path)

    def execute(self):
        return subprocess.call([self.path])

    def replace_extension(self, new_extension='txt'):
        """Return a new path with the extension swapped out."""
        return FilePath(os.path.splitext(self.path)[0] + '.' + new_extension)

    def new_name_insert(self, string):
        """Return a new name by appending a string before the extension."""
        return self.prefix_path + "." + string + self.extension

    def make_directory(self):
        """Create the directory the file is supposed to be in if it does not exist."""
        if not self.directory.exists: self.directory.create()

    def must_exist(self):
        """Raise an exception if the path doesn't exist."""
        if not self.exists: raise Exception("The file path '%s' does not exist." % self.path)

    def head(self, lines=10):
        """Return the first few lines."""
        content = FilePath.__iter__(self)
        for x in xrange(lines):
            yield content.next()

    def tail(self, lines=20):
        """Return the last few lines."""
        from autopaths.common import tail
        return tail(self.path, lines=lines)

    def move_to(self, path):
        """Move the file."""
        # Special directory case, keep the same name (put it inside) #
        if path.endswith(sep): path = path + self.filename
        # Normal case #
        assert not os.path.exists(path)
        shutil.move(self.path, path)
        # Update the internal link #
        self.path = path

    def rename(self, new_name):
        """Rename the file but leave it in the same directory."""
        assert sep not in new_name
        path = self.directory + new_name
        assert not os.path.exists(path)
        shutil.move(self.path, path)
        # Update the internal link #
        self.path = path

    def link_from(self, path, safe=False):
        """Make a link here pointing to another file somewhere else.
        The destination is hence self.path and the source is *path*."""
        # Get source and destination #
        source      = path
        destination = self.path
        # Windows doesn't have os.symlink #
        if os.name == "posix": self.symlinks_on_linux(  source, destination, safe)
        if os.name == "nt":    self.symlinks_on_windows(source, destination, safe)

    def link_to(self, path, safe=False, absolute=True):
        """Create a link somewhere else pointing to this file.
        The destination is hence *path* and the source is self.path."""
        # If source is a file and the destination is a dir, put it inside #
        if path.endswith(sep): path = path + self.filename
        # Get source and destination #
        if absolute: source = self.absolute_path
        else:        source = self.path
        destination = path
        # Windows doesn't have os.symlink #
        if os.name == "posix": self.symlinks_on_linux(  source, destination, safe)
        if os.name == "nt":    self.symlinks_on_windows(source, destination, safe)

    def symlinks_on_linux(self, source, destination, safe):
        # Do it unsafely #
        if not safe:
            if os.path.exists(destination): os.remove(destination)
            os.symlink(source, destination)
        # Do it safely #
        if safe:
            try: os.remove(destination)
            except OSError: pass
            try: os.symlink(source, destination)
            except OSError: pass

    def symlinks_on_windows(self, source, destination, safe):
        """Yes, source and destination need to be in the reverse order."""
        import win32file
        win32file.CreateSymbolicLink(destination, source, 0)

    def gzip_to(self, path=None):
        """Make a gzipped version of the file at a given path."""
        if path is None: path = self.path + ".gz"
        with open(self.path, 'rb') as orig_file:
            with gzip.open(path, 'wb') as new_file:
                new_file.writelines(orig_file)
        return FilePath(path)

    def ungzip_to(self, path=None, mode='w'):
        """Make an unzipped version of the file at a given path."""
        if path is None: path = self.path[:3]
        with gzip.open(self, 'rb') as orig_file:
            with open(path, mode) as new_file:
                new_file.writelines(orig_file)
        return FilePath(path)

    def zip_to(self, path=None):
        """Make a zipped version of the file at a given path."""
        pass

    def unzip_to(self, destination=None, inplace=False, single=True):
        """Unzip a standard zip file. Can specify the destination of the
        uncompressed file, or just set inplace=True to delete the original."""
        # Check #
        assert zipfile.is_zipfile(self.path)
        # Load #
        z = zipfile.ZipFile(self.path)
        if single or inplace: assert len(z.infolist()) == 1
        # Single file #
        if single:
            member = z.infolist()[0]
            tmpdir = tempfile.mkdtemp() + sep
            z.extract(member, tmpdir)
            z.close()
            if inplace: shutil.move(tmpdir + member.filename, self.directory + member.filename)
            else:       shutil.move(tmpdir + member.filename, destination)
        # Multifile - no security, dangerous - Will use CWD if dest is None!! #
        # If a file starts with an absolute path, will overwrite your files anywhere #
        if not single:
            z.extractall(destination)

    def targz_to(self, path=None):
        """Make a targzipped version of the file at a given path."""
        pass

    def untargz_to(self, destination=None, inplace=False):
        """Make an untargzipped version of the file at a given path"""
        import tarfile
        archive = tarfile.open(self.path, 'r:gz')
        archive.extractall(destination)

    def append(self, what):
        """Append some text or an other file to the current file"""
        if isinstance(what, FilePath): what = what.contents
        autopaths.common.append_to_file(self.path, what)

    def prepend(self, what):
        """Append some text or an other file to the current file"""
        if isinstance(what, FilePath): what = what.contents
        autopaths.common.prepend_to_file(self.path, what)