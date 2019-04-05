from setuptools import setup

setup(
        name             = 'autopaths',
        version          = '1.2.0',
        description      = 'autopaths is a python package for dealing with file paths and automation.',
        long_description = open('README.md').read(),
        license          = 'MIT',
        url              = 'http://github.com/xapple/autopaths/',
        author           = 'Lucas Sinclair',
        author_email     = 'lucas.sinclair@me.com',
        install_requires = ['sh'],
        packages         = ['autopaths'],
    )
