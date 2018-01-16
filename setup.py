import os
from setuptools import setup, find_packages

requirements = open(os.path.join(os.path.dirname(__file__),
                                 'requirements.txt')).readlines()

packages = find_packages()

setup (
    name='hspsdb',
    version='0.0.2',
    packages=find_packages(),
    install_requires=requirements,
    long_description = 'Index scripts for sequence similarity search results '
                       'either in NCBI-BLAST xml/json formats, tabular format, '
                       'or in SAM/BAM formats'
)
