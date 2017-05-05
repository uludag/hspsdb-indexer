#!/usr/bin/env python
""" Index sample BAM files included in the project """
from __future__ import print_function

import argparse, os

from elasticsearch import Elasticsearch

from indexbam import index as indexbam

if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    testfiles = [
        "./src/test/resources/htsjdk/samtools/compressed.bam",
        "./testdb/kallistosearch/kallisto-sample-pseudoaligned.bam",
        "./testdb/bwamethsearch/bwamethexamplesearch.bam"
    ]
    argsdef = argparse.ArgumentParser(
        description='Index test files with Elasticsearch')
    argsdef.add_argument('--index',
                        default="hspsdb",
                        help='name of the elasticsearch index')
    argsdef.add_argument('--host', default="bio2rdf",
                        help='Elasticsearch server hostname')
    argsdef.add_argument('--port', default="9200",
                        help="Elasticsearch server port")
    args = argsdef.parse_args()
    host = args.host
    port = args.port
    con = Elasticsearch(host=host, port=port, timeout=600)
    for bamfile in testfiles:
        bamfile = os.path.join(d, '../..', bamfile)
        indexbam(con, bamfile, args.index)
