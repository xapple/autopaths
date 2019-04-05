# Built-in modules #
import os, tempfile, subprocess, shutil, codecs, gzip, zipfile, datetime

# Internal modules #
import autopaths

# Third party modules #
if os.name == "posix": import sh
if os.name == "nt":    import pbs

# Constants #
if os.name == "posix": sep = "/"
if os.name == "nt":    sep = "\\"

################################################################################
class FilePath(autopaths.base_path.BasePath):
    """Represents a string to a file path and adds methods to interact with
    files on disk.

    I can never remember all those darn `os.path` commands, so I made a class
    that wraps them with an easier and more pythonic syntax.

        path = FilePath('/home/root/text.txt')
        print path.extension
        print path.directory
        print path.filename

    You can find lots of the common things you would need to do with file paths.
    Such as: path.make_executable() etc etc."""

    def __nonzero__(self): return self.path != None and self.count_bytes != 0

    def __list__(self):    return self.count

    def __iter__(self):
        # Maybe do not overwrite iter()? #
        with open(self.path, 'r') as handle:
            for line in handle: yield line

    def __len__(self):
        if self.path is None: return 0
        return self.count

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

    # ------------------------------ Properties ----------------------------- #
    @property
    def first(self):
        """Just the first line. Don't try this on binary files."""
        with open(self.path, 'r') as handle:
            for line in handle: return line

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
    def md5(self):
        """Compute the md5 of a file. Pretty fast."""
        md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(blocksize), ""):
                md5.update(block)
        return md5.hexdigest()

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
        """Copy to a different path."""
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

    def head(self, num_lines=10):
        """Return the first few lines."""
        lines = iter(self)
        for x in xrange(num_lines): yield lines.next()

    def tail(self, lines=20):
        """Return the last few lines."""
        # Constant #
        buffer_size = 1024
        # Smart algorithm #
        with open(self.path, 'r') as handle:
            handle.seek(0, 2)
            num_bytes = handle.tell()
            size      = lines + 1
            block     = -1
            data      = []
            # Loop #
            while size > 0 and num_bytes > 0:
                if num_bytes - buffer_size > 0:
                    # Seek back one whole buffer_size #
                    handle.seek(block * buffer_size, 2)
                    # Read buffer #
                    data.insert(0, handle.read(buffer_size))
                else:
                    # File too small, start from beginning #
                    handle.seek(0,0)
                    # Only read what was not read #
                    data.insert(0, handle.read(num_bytes))
                lines_found = data[0].count('\n')
                size       -= lines_found
                num_bytes  -= buffer_size
                block      -= 1
            # Return #
            for line in ''.join(data).splitlines()[-lines:]: yield line

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

    #------------------------------ Compression ------------------------------#
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

    #-------------------------------- Modify ---------------------------------#
    def append(self, data):
        """Append some text or an other file to the current file"""
        if isinstance(data, FilePath): data = data.contents
        with open(path, "a") as handle: handle.write(data)

    def prepend(self, data, buffer_size=1 << 15):
        """Prepend some text or an other file to the current file.
        TODO:
        * Add a random string to the backup file.
        * Restore permissions after copy.
        """
        # Check there is something to prepend #
        assert data
        # Support passing other files #
        if isinstance(data, FilePath): data = data.contents
        # Create a new file #
        result_file = autopaths.tmp_path.new_temp_file()
        # Open input/output files #
        # Note: output file's permissions lost #
        with open(self) as in_handle:
            with open(result_file, 'w') as out_handle:
                while data:
                    out_handle.write(data)
                    data = in_handle.read(buffer_size)
        # Switch the files around #
        self.remove()
        result_file.move_to(self)

    def remove_line(self, line_to_remove):
        """Search the file for a given line, and if found, remove it."""
        # Check there is something to remove #
        assert line_to_remove
        # Create a new file #
        result_file = autopaths.tmp_path.new_temp_file()
        # Open input/output files #
        # Note: output file's permissions lost #
        result_file.writelines(line for line in self if line != line_to_remove)
        # Switch the files around #
        self.remove()
        result_file.move_to(self)
