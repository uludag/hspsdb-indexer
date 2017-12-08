import os
from setuptools import setup, find_packages

requirements = open(os.path.join(os.path.dirname(__file__),
                                 'requirements.txt')).readlines()

packages = find_packages()

setup (
       name='hspsdb-indexer',
       version='0.0.1',
       packages=find_packages(),
       install_requires=requirements,
       long_description = 'Index scripts for sequence similarity search results '
                          'in NCBI-BLAST json/xml2 formats or in SAM/BAM formats'
)
