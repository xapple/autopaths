# Built-in modules #
import os, hashlib, re

###############################################################################
def natural_sort(item):
    """
    Sort strings that contain numbers correctly. Works in Python 2 and 3.

    >>> l = ['v1.3.12', 'v1.3.3', 'v1.2.5', 'v1.2.15', 'v1.2.3', 'v1.2.1']
    >>> l.sort(key=natural_sort)
    >>> l.__repr__()
    "['v1.2.1', 'v1.2.3', 'v1.2.5', 'v1.2.15', 'v1.3.3', 'v1.3.12']"
    """
    dre = re.compile(r'(\d+)')
    return [int(s) if s.isdigit() else s.lower() for s in re.split(dre, item)]

###############################################################################
def prepend_to_file(path, data, bufsize=1<<15):
    """TODO:
    * Add a random string to the backup file.
    * Restore permissions after copy.
    """
    # Backup the file #
    backupname = path + os.extsep + 'bak'
    # Remove previous backup if it exists #
    try: os.unlink(backupname)
    except OSError: pass
    os.rename(path, backupname)
    # Open input/output files, note: outputfile's permissions lost #
    with open(backupname) as inputfile:
        with open(path, 'w') as outputfile:
            outputfile.write(data)
            buf = inputfile.read(bufsize)
            while buf:
                outputfile.write(buf)
                buf = inputfile.read(bufsize)
    # Remove backup on success #
    os.remove(backupname)

###############################################################################
def append_to_file(path, data):
    with open(path, "a") as handle:
        handle.write(data)

###############################################################################
def md5sum(file_path, blocksize=65536):
    """Compute the md5 of a file. Pretty fast."""
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(blocksize), ""):
            md5.update(block)
    return md5.hexdigest()

################################################################################
def tail(path, lines=20):
    with open(path, 'r') as f:
        BUFSIZ = 1024
        f.seek(0, 2)
        num_bytes = f.tell()
        size = lines + 1
        block = -1
        data = []
        while size > 0 and num_bytes > 0:
            if num_bytes - BUFSIZ > 0:
                # Seek back one whole BUFSIZ
                f.seek(block * BUFSIZ, 2)
                # Read BUFFER
                data.insert(0, f.read(BUFSIZ))
            else:
                # File too small, start from beginning
                f.seek(0,0)
                # Only read what was not read
                data.insert(0, f.read(num_bytes))
            lines_found = data[0].count('\n')
            size -= lines_found
            num_bytes -= BUFSIZ
            block -= 1
        return '\n'.join(''.join(data).splitlines()[-lines:])
