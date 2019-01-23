# Built-in modules #
import os, hashlib

################################################################################
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

################################################################################
def append_to_file(path, data):
    with open(path, "a") as handle:
        handle.write(data)

################################################################################
def md5sum(file_path, blocksize=65536):
    """Compute the md5 of a file. Pretty fast."""
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(blocksize), ""):
            md5.update(block)
    return md5.hexdigest()
