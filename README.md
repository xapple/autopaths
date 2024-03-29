[![PyPI version](https://badge.fury.io/py/autopaths.svg)](https://badge.fury.io/py/autopaths)

# `autopaths` version 1.6.0

`autopaths` is a python package for dealing with file paths and automation.

It has many convenience methods that apply to directory paths and/or file paths and contains several submodules that are useful when building pipelines. See below for examples and documentation.

## Prerequisites

Since `autopaths` is written in python, it is compatible with all operating systems: Linux, macOS and Windows. The only prerequisite is `python3` (which is often installed by default) along with the `pip3` package manager.

To check if you have `python3` installed, type the following on your terminal:

    $ python3 -V

If you do not have `python3` installed, please refer to the section [obtaining python3](docs/installing_tips.md#obtaining-python3).

To check you have `pip3` installed, type the following on your terminal:

    $ pip3 -V

If you do not have `pip3` installed, please refer to the section [obtaining pip3](docs/installing_tips.md#obtaining-pip3).

## Installing

To install the `autopaths` package, simply type the following commands on your terminal:

    $ pip3 install --user autopaths

Alternatively, if you want to install it for all users of the system:

    $ sudo pip3 install autopaths

## Usage

Bellow are some examples to illustrate the various ways there are to use this package.


### `FilePath` object

Here are a few example usages of this object:

    from autopaths.file_path import FilePath
    f = FilePath("input/raw/reads_56.fastq")
    print(f.exists)
    print(f.extension)
    print(f.size)
    print(f.contains_binary)
    f.prepend('# This file was backed-up\n')
    f.gzip_to('backup/old_reads/reads_56.fastq.gz')
    f.move_to(f.parent)

As you can see, once you have created a FilePath, many useful methods are available. No more need for long `os.path` or `shutil` commands of which you can never remember the syntax.

To see the complete list of utility methods and properties, look at the source code. You can find lots of the common things you would need to do with file paths such as `f.make_executable()` etc. right at your fingertips.

### `DirectoryPath` object

Similar to a file path object. Here is an example usage of this object:

    from autopaths.dir_path import DirectoryPath
    d = DirectoryPath("cleaned/reads/")
    print(d.mod_time)
    d.create_if_not_exists()
    f = d + 'new.fastq'

### `AutoPaths` object

You can use this class like this when making pipelines to quickly refer to a predefined file path with a simple attribute lookup. This example explains it:

    class Sample(object):
        all_paths = """
                    /raw/raw.sff
                    /raw/raw.fastq
                    /clean/trim.fastq
                    /clean/clean.fastq
                    """

        def __init__(self, base_dir):
            from autopaths.auto_paths import AutoPaths
            self.p = AutoPaths(base_dir, self.all_paths)

        def clean(self):
            shutil.move(self.p.raw_sff, self.p.clean_fastq)

## Extra documentation

More documentation is available at:

<http://xapple.github.io/autopaths/autopaths>

This documentation is simply generated with:

    $ pdoc --html --output-dir docs --force autopaths