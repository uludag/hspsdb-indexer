#!/usr/bin/env python
""" Index SAM BAM test files included in the project """
from __future__ import print_function
import unittest
import argparse, os

from elasticsearch import Elasticsearch

from hspsdb import indexbam

INDEX = "hspsdb-tests"
d = os.path.dirname(os.path.abspath(__file__))


def test_index_pybam():  # index_pybam() supports Elasticsearch only
    testfiles = [
        "../src/test/resources/htsjdk/samtools/compressed.bam",
        "../testdb/kallistosearch/kallisto-sample-pseudoaligned.bam"
        # "../testdb/bwamethsearch/bwamethexamplesearch.bam"
    ]
    for bamfile in testfiles:
        bamfile = os.path.join(d, bamfile)
        indexbam.index_pybam(bamfile, INDEX)

def test_index_pysam():  # index_pysam() supports MongoDB only
    testfiles = [
        "../src/test/resources/mbsearch/SRR317068-pairedfastq-search.sam",
        "../src/test/resources/htsjdk/samtools/uncompressed.sam",
        "../src/test/resources/htsjdk/samtools/unsorted.sam"
    ]
    for samfile in testfiles:
        samfile = os.path.join(d, samfile)
        indexbam.index_pysam("MongoDB", samfile, INDEX, "tests")


if __name__ == '__main__':
    unittest.main()
