# `autopaths` version 1.0.1

`autopaths` is a python package for dealing with file paths and automation.

It contains several submodules that are useful when building pipelines. See below for examples and documentation.

# FilePath object

Here is an example usage of this object:

    from autopaths.file_path import FilePath
    f = FilePath("input/raw/reads_56.fastq")
    print(f.exists)
    print(f.extension)
    print(f.size)
    f.append('This file was backed-up\n')
    f.gzip_to('backup/old_reads/reads_56.fastq')

As you can see once you have created a FilePath, many useful methods are available. No more need for long `os.path` or `shutil` commands of which you can never remember the syntax.

To see the complete list, look at the source code.

# DirectoryPath object

Similar to a file path object. Here is an example usage of this object:

    from autopaths.dir_path import DirectoryPath
    d = DirectoryPath("cleaned/reads/")
    print(d.mod_time)
    d.create_if_not_exists()

# AutoPaths object

This part of the documentation should be written soon.