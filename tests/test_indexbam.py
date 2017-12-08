#!/usr/bin/env python
""" Index sample BAM files included in the project """
from __future__ import print_function
import unittest
import argparse, os

from elasticsearch import Elasticsearch

from hspsdb import indexbam

ES_INDEX = "hspsdb"

def test_index():
    d = os.path.dirname(os.path.abspath(__file__))
    testfiles = [
        "../src/test/resources/htsjdk/samtools/compressed.bam",
        "../testdb/kallistosearch/kallisto-sample-pseudoaligned.bam",
        "../testdb/bwamethsearch/bwamethexamplesearch.bam"
    ]
    for bamfile in testfiles:
        bamfile = os.path.join(d, bamfile)
        indexbam.index(bamfile, ES_INDEX)

if __name__ == '__main__':
    unittest.main()
