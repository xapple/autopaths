[![PyPI version](https://badge.fury.io/py/autopaths.svg)](https://badge.fury.io/py/autopaths)
[![changelog](http://allmychanges.com/p/python/autopaths/badge/)](http://allmychanges.com/p/python/autopaths/?utm_source=badge)

# `autopaths` version 1.2.0

`autopaths` is a python package for dealing with file paths and automation.

It contains several submodules that are useful when building pipelines. See below for examples and documentation.

# `FilePath` object

Here are a few example usages of this object:

    from autopaths.file_path import FilePath
    f = FilePath("input/raw/reads_56.fastq")
    print(f.exists)
    print(f.extension)
    print(f.size)
    print(f.contains_binary)
    f.prepend('# This file was backed-up\n')
    f.gzip_to('backup/old_reads/reads_56.fastq')
    f.move_to(f.parent)
    f.make_executable()

As you can see, once you have created a FilePath, many useful methods are available. No more need for long `os.path` or `shutil` commands of which you can never remember the syntax.

To see the complete list of utility methods and properties, look at the source code. You can find lots of the common things you would need to do with file paths `f.make_executable()` etc etc.

# `DirectoryPath` object

Similar to a file path object. Here is an example usage of this object:

    from autopaths.dir_path import DirectoryPath
    d = DirectoryPath("cleaned/reads/")
    print(d.mod_time)
    d.create_if_not_exists()
    f = d + 'new.fastq'

# `AutoPaths` object

You can use this class like this when making pipelines to quickly refer to a predefined file path with a simple attribute lookup. This example explains it:

    class Sample(object):
        all_paths = '''
            /raw/raw.sff
            /raw/raw.fastq
            /clean/trim.fastq
            /clean/clean.fastq'''

        def __init__(self, base_dir):
            self.p = AutoPaths(base_dir, self.all_paths)

        def clean(self):
            shutil.move(self.p.raw_sff, self.p.clean_fastq)
