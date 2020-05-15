from setuptools import setup, find_packages

setup(
        name             = 'autopaths',
        version          = '1.4.0',
        description      = 'autopaths is a python package for dealing with file paths and automation.',
        long_description = open('README.md').read(),
        long_description_content_type = 'text/markdown',
        license          = 'MIT',
        url              = 'http://github.com/xapple/autopaths/',
        author           = 'Lucas Sinclair',
        author_email     = 'lucas.sinclair@me.com',
        packages         = find_packages(),
        install_requires = ['six'],
    )
