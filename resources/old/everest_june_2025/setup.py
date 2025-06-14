###############################################################################
''''''
###############################################################################
from setuptools import setup, find_packages
from numpy.distutils.core import setup
from os import path
import io

## instructions for upload to pypi

this_directory = path.abspath(path.dirname(__file__))
with io.open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

if __name__ == "__main__":
    setup(name = 'everest',
          author            = "Rohan Byrne",
          author_email      = "rohan.byrne@gmail.com",
          url               = "https://github.com/rsbyrne/everest",
          version           = "0.9",
          description       = "A file format and associated Python tools for computational suite modelling",
          long_description  = long_description,
          long_description_content_type='text/markdown',
          packages          = ['everest'],
          install_requires  = ['simpli','funcy'],
          setup_requires    = [''],

          
          
          classifiers       = ['Programming Language :: Python :: 3',
                               'Programming Language :: Python :: 3.3',
                               'Programming Language :: Python :: 3.4',
                               'Programming Language :: Python :: 3.5',
                               'Programming Language :: Python :: 3.6',
                               'Programming Language :: Python :: 3.7',
                               'Programming Language :: Python :: 3.8',]
          )

###############################################################################
''''''
###############################################################################
