#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair.
MIT Licensed.
Contact at www.sinclair.bio
"""

# Built-in modules #
import os, tempfile, subprocess, shutil, gzip, zipfile, hashlib

# Internal modules #
import autopaths
from autopaths.common import pad_extra_whitespace

# Constants #
if os.name == "posix": sep = "/"
if os.name == "nt":    sep = "\\"

################################################################################
class FilePath(autopaths.base_path.BasePath):
    """
    Holds a string pointing to a file path and adds methods to interact with
    files on disk.

    I can never remember all those darn `os.path` commands, so I made a class
    that wraps them with an easier and more pythonic syntax.

        path = FilePath('/home/root/text.txt')
        print path.extension
        print path.directory
        print path.filename

    You can find lots of the common things you would need to do with file paths.
    Such as: path.make_executable() etc etc.
    """

    def __bool__(self): return self.path is not None and self.count_bytes != 0

    def __iter__(self):
        with open(self.path, 'r', encoding='utf-8') as handle:
            for line in handle: yield line

    def __len__(self):
        if self.path is None: return 0
        return self.count

    def __sub__(self, directory):
        """
        Subtract a directory from the current path to get the relative path
        of the current file from that directory.
        """
        return os.path.relpath(self.path, directory)

    def __enter__(self):
        """Called when entering the 'with' statement (context manager)."""
        return self.open()

    def __exit__(self, err_type, value, traceback):
        """
        Called when exiting the 'with' statement.
        This enables us to close the file or database properly, even when
        exceptions are raised.
        """
        self.close()

    # ------------------------------ Properties ----------------------------- #
    @property
    def first(self):
        """Just the first line. Don't try this on binary files."""
        with open(self.path, 'r') as handle:
            for line in handle: return line

    @property
    def prefix_path(self):
        """The full path without the last extension and trailing period."""
        return str(os.path.splitext(self.path)[0])

    @property
    def prefix(self):
        """Just the filename without the last extension and trailing period."""
        return str(os.path.basename(self.prefix_path))

    @property
    def extension(self):
        """Just the last extension without the trailing period."""
        if '.' not in self.filename:
            raise Exception("The file '%s' has no extension." % self.path)
        return self.filename.split('.')[-1]

    @property
    def name(self):
        """Shortcut for self.filename."""
        return self.filename

    @property
    def filename(self):
        """Just the filename with the extension."""
        return str(os.path.basename(self.path))

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
        # Third party modules #
        if os.name == "posix": import sh
        if os.name == "nt":    import pbs3
        # Count lines #
        if os.name == "posix":
            return int(sh.wc('-l', self.path).split()[0])
        if os.name == "nt":
            return int(pbs3.Command("find")('/c', '/v', '""', self.path))

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
        with open(self.path, encoding='utf8') as handle:return handle.read()

    @property
    def md5(self):
        """Compute the md5 of a file. Pretty fast."""
        md5 = hashlib.md5()
        with open(self.path, "rb") as f:
            for block in iter(lambda: f.read(4096), b""):
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

    @property
    def magic_number(self):
        """Return the first four bytes of the file."""
        with open(self.path, 'rb') as f: return f.read(4)

    @property
    def lines(self):
        """Get all lines in a list with \n striped."""
        with open(self.path, 'r', encoding='utf-8') as handle:
            return [line.strip('\n') for line in handle]

    #-------------------------------- Methods --------------------------------#
    def read(self, encoding=None):
        with open(self.path, 'r', encoding) as handle: content = handle.read()
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
            with open(self.path, mode, encoding=encoding) as handle:
                handle.write(content)

    def writelines(self, content, encoding=None, mode='w'):
        if encoding is None:
            with open(self.path, mode) as handle: handle.writelines(content)
        else:
            with open(self.path, mode, encoding=encoding) as handle:
                handle.writelines(content)

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
        """
        Create the directory the file is supposed to be in if it does not
        exist.
        """
        if not self.directory.exists: self.directory.create()

    def must_exist(self):
        """Raise an exception if the path doesn't exist."""
        if not self.exists:
            raise Exception("The file path '%s' does not exist." % self.path)

    def head(self, num_lines=20):
        """Yield the first few lines."""
        lines = iter(self)
        for _ in range(num_lines): yield next(lines)

    @property
    def pretty_head(self):
        return "\n" + pad_extra_whitespace("\n".join(self.head()), 4) + "\n"

    def tail(self, num_lines=20, encoding='utf-8'):
        """Yield the last few lines of the file."""
        # Constant #
        buffer_size = 1024
        # Smart algorithm #
        with open(self.path, 'rb') as handle:
            handle.seek(0, 2)
            num_bytes = handle.tell()
            size      = num_lines + 1
            block     = -1
            data      = []
            # Loop #
            while size > 0 and num_bytes > 0:
                if num_bytes - buffer_size > 0:
                    # Seek back one whole buffer_size #
                    handle.seek(block * buffer_size, os.SEEK_END)
                    # Read buffer #
                    data.insert(0, handle.read(buffer_size).decode(encoding))
                else:
                    # File too small, start from beginning #
                    handle.seek(0,0)
                    # Only read what was not read #
                    data.insert(0, handle.read(num_bytes).decode(encoding))
                lines_found = data[0].count('\n')
                size       -= lines_found
                num_bytes  -= buffer_size
                block      -= 1
            # Return #
            for line in ''.join(data).splitlines()[-num_lines:]: yield line

    @property
    def pretty_tail(self):
        return "\n" + pad_extra_whitespace("\n".join(self.tail()), 4) + "\n"

    def move_to(self, path, overwrite=False):
        """Move the file to a new location."""
        # Parse the path #
        path = autopaths.Path(path)
        # Special directory case, keep the same name (put it inside) #
        if path.endswith(sep): path = path + self.filename
        # Check that the directory exists #
        path.directory.create_if_not_exists()
        # Normal case #
        if os.path.exists(path) and overwrite: os.remove(path)
        assert not os.path.exists(path)
        shutil.move(self.path, path)
        # Update the internal link #
        self.path = path
        # Return #
        return path

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
        # Case where path is not specified #
        if path is None: path = self.path + ".gz"
        # Do it #
        with open(self.path, 'rb') as orig_file:
            with gzip.open(path, 'wb') as new_file:
                new_file.writelines(orig_file)
        # Return #
        return FilePath(path)

    def ungzip_to(self, path=None, mode='wb'):
        """Make an unzipped version of the file at a given path."""
        # Case where path is not specified #
        if path is None: path = self.path[:-3]
        # Do it #
        with gzip.open(self, 'rb') as orig_file:
            with open(path, mode) as new_file:
                new_file.writelines(orig_file)
        # Return #
        return FilePath(path)

    def zip_to(self, path=None):
        """Make a zipped version of the file at a given path."""
        pass

    def unzip_to(self, path=None, inplace=False, single=True):
        """
        Unzip a standard zip file. Can specify the destination of the
        uncompressed file, or just set inplace=True to delete the original.
        """
        # Parse the path #
        path = autopaths.Path(path)
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
            if inplace: shutil.move(tmpdir + member.filename,
                                    self.directory + member.filename)
            else:       shutil.move(tmpdir + member.filename,
                                    path)
        # Multifile - no security, dangerous - Will use CWD if dest is None!!
        # If a file starts with an absolute path, will overwrite your files
        # anywhere
        if not single:
            z.extractall(path)
            return autopaths.dir_path.DirectoryPath(path)
        # Return #
        return FilePath(path)

    def targz_to(self, path=None):
        """Make a targzipped version of the file at a given path."""
        pass

    def untargz_to(self, path=None):
        """Make an untargzipped version of the file at a given path."""
        # Case where path is not specified #
        if path is None:
            if   self.path.endswith('.tgz'):    path = self.path[:-4]
            elif self.path.endswith('.tar.gz'): path = self.path[:-7]
            else: path = self.path + '.untargz'
        # Do it #
        import tarfile
        with tarfile.open(self.path, 'r:gz') as archive:
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(archive, path)
        # Return #
        return autopaths.dir_path.DirectoryPath(path + '/')

    def tar_to(self, path=None):
        """Make a tared version of the file at a given path."""
        pass

    def untar_to(self, path=None):
        """Make an untared version of the file at a given path."""
        # Case where path is not specified #
        if path is None:
            if   self.path.endswith('.tgz'):    path = self.path[:-4]
            elif self.path.endswith('.tar.gz'): path = self.path[:-7]
            else: path = self.path + '.untargz'
        # Do it #
        import tarfile
        with tarfile.open(self.path) as archive:
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(archive, path)
        # Return #
        return autopaths.dir_path.DirectoryPath(path + '/')

    #-------------------------------- Modify ---------------------------------#
    def append(self, data):
        """Append some text or an other file to the current file."""
        if isinstance(data, FilePath): data = data.contents
        with open(self.path, "a") as handle: handle.write(data)

    def prepend(self, data, buffer_size=1 << 15):
        """
        Prepend some text or an other file to the current file.
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
        # Open input/output files, note: output file's permissions lost #
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
        # Open input/output files, note: output file's permissions lost #
        result_file.writelines(line for line in self if line != line_to_remove)
        # Switch the files around #
        self.remove()
        result_file.move_to(self)

    def remove_first_line(self):
        """
        Remove the first line of the file.
        Equivalent to sh.sed('-i', '1d', self.path)
        """
        # Create a new file #
        result_file = autopaths.tmp_path.new_temp_file()
        # Open input/output files, note: output file's permissions lost #
        all_lines = iter(self)
        next(all_lines)
        result_file.writelines(all_lines)
        # Switch the files around #
        self.remove()
        result_file.move_to(self)

    def replace_line(self, line_to_remove, line_to_insert, safe=False):
        """
        Search the file for a given line, and if found,
        replace it with another line.
        """
        # Check the line endings #
        line_to_remove = line_to_remove.strip('\n')
        line_to_insert = line_to_insert.strip('\n')
        # Create a new file #
        result_file = autopaths.tmp_path.new_temp_file()
        # Generate the lines #
        def new_lines():
            found = False
            for line in self:
                if line.rstrip() == line_to_remove.rstrip():
                    yield line_to_insert.rstrip() + '\n'
                    found = True
                else: yield line
            if found is False and safe is False:
                msg = "The line to replace ('%s') was not found in '%s'"
                raise Exception(msg % (line_to_remove, self.path))
        # Open input/output files, note: output file's permissions lost #
        result_file.writelines(new_lines())
        # Switch the files around #
        self.remove()
        result_file.move_to(self)

    def replace_word(self, word_to_find, replacement_word):
        """
        Search the file for a given word, and if found,
        replace every occurrence of it with another word.
        """
        # Create a new file #
        result_file = autopaths.tmp_path.new_temp_file()
        # Generate the lines #
        def new_lines():
            for line in self:
                yield line.replace(word_to_find, replacement_word)
        # Open input/output files, note: output file's permissions lost #
        result_file.writelines(new_lines())
        # Switch the files around #
        self.remove()
        result_file.move_to(self)

    #---------------------------- External tools -----------------------------#
    def sed_replace(self, before, after):
        if os.name == "posix":
            import sh
            return sh.sed('-i', 's/%s/%s/' % (before, after), self.path)
        if os.name == "nt":
            import pbs3
            sed_cmd = 'sed -i "s/%s/%s/" %s' % (before, after, self.path)
            return pbs3.bash('-c', "'" + sed_cmd + "'" )
