#!/usr/bin/env python2
""" Index given SAM or BAM file with Elasticsearch or MongoDB
    [this work is at early stages of development]
 """

from __future__ import print_function

import argparse
import json
import os
from pprint import pprint

import pysam
from elasticsearch.helpers import streaming_bulk
from nosqlbiosets.dbutils import DBconnection
from pymongo.errors import BulkWriteError
from pymongo.operations import ReplaceOne

from pybam import pybam

CHUNK_SIZE = 1024

def getcigar(a):
    c = ""
    if len(a) == 0: c = "*"
    for pair in a:
        c += str(pair[1])
        c += pair[0]
    return c

# attrs = ['readName', 'flags', 'referenceName', 'alignmentStart',
#          'mappingQuality', 'cigarString', 'mateReferenceName',
#          'readLength']

# TODO: Index headers and reference to reference-sequences
class BAMReader:

    def __init__(self, infile):
        self.infile = infile
        self.i = 0

    def read_pybam(self):
        parser = ['sam_qname', 'sam_flag', 'sam_refID', 'sam_pos1',
                  'sam_mapq', 'sam_cigar_string',
                  'sam_next_refID', 'sam_pnext1', 'sam_tlen', 'sam_seq',
                  'sam_l_read_name']
        print("Reading input file '%s' for indexing" % self.infile)
        pure_bam = pybam.read(self.infile, parser)
        print("Reference sequence names with lengths:")
        print(pure_bam.file_chromosome_lengths)
        for read in pure_bam:
            self.i += 1
            r = dict()
            # TODO: Can we use attrs array above
            r['readName'] = read[0]
            r['flags'] = read[1]
            refid = read[2]
            if refid < 0:
                refname = 'Unmapped'
            else:
                refname = pure_bam.file_chromosomes[refid]
            r['referenceName'] = refname
            r['alignmentStart'] = read[3]
            r['mappingQuality'] = read[4]
            r['cigarString'] = read[5]
            r['mateReferenceName'] = pure_bam.file_chromosomes[read[6]]
            r['mateAlignmentStart'] = read[7]
            r['readLength'] = read[8]
            # TODO: readSequence vs readString (check htsjdk library)
            r['readString'] = read[9]
            r['filename'] = self.infile
            r['_id'] = self.infile + str(self.i)
            yield r


def elasticsearch_settings():
    d = os.path.dirname(os.path.abspath(__file__))
    m = json.load(open(d + "/../scripts/mappings-sam.json", "r"))
    s = {"index": {
        "number_of_shards": "5",
        "number_of_replicas": "0",
        "refresh_interval": -1
    }}
    return m, s


# Index input BAM file, use pybam library for reading the input BAM file
def index_pybam(infile, index, host=None, port=None):
    m, s = elasticsearch_settings()
    esc = DBconnection("Elasticsearch", index, host=host, port=port,
                       es_indexmappings=m, es_indexsettings=s,
                       recreateindex=True).es
    i = BAMReader(infile)
    for ok, result in streaming_bulk(
            esc,
            i.read_pybam(),
            index=index,
            doc_type='sam',
            chunk_size=CHUNK_SIZE
    ):
        action, result = result.popitem()
        doc_id = '/%s/commits/%s' % (index, result['_id'])
        if not ok:
            print('Failed to %s document %s: %r' % (action, doc_id, result))
    esc.indices.refresh(index=index)
    return i.i


# Index input SAM/BAM file, use pysam library for reading the input file
def index_pysam(db, infile, index, collection, host=None, port=None,
                check_header=True, check_sq=True):
    if db != "MongoDB":
        print("Only MongoDB support has been implemented")
        exit(-1)
    mdbi = DBconnection(db, index).mdbi
    i = 0
    entries = list()
    with open(infile) as samfile:
        print(infile)
        inf = pysam.AlignmentFile(samfile, "r", check_header=check_header,
                                  check_sq=check_sq)
        try:
            for read in inf:
                i += 1
                r = dict()
                r['readName'] = read.qname
                r['flags'] = read.flag
                if read.reference_id == -1:
                    continue
                r['referenceName'] = read.reference_name
                r['alignmentStart'] = read.query_alignment_start
                r['mappingQuality'] = read.mapping_quality
                r['cigarString'] = read.cigarstring
                r['mateReferenceName'] = read.mrnm  # CHECK ME
                r['mateAlignmentStart'] = read.mpos
                r['readLength'] = read.query_length
                r['readString'] = read.query_sequence
                r['filename'] = infile
                r['_id'] = infile + str(i)
                entries.append(ReplaceOne({'_id':r['_id']}, r, upsert=True))
                if len(entries) == CHUNK_SIZE:
                    mdbi[collection].bulk_write(entries, ordered=False,
                                                bypass_document_validation=True)
                    entries = list()
            if len(entries) > 0:
                mdbi[collection].bulk_write(entries, ordered=False,
                                            bypass_document_validation=True)
        except BulkWriteError as e:
            pprint(e)
            pprint(e.details)
            exit()
    return


if __name__ == '__main__':
    argsdef = argparse.ArgumentParser(
        description='Index given SAM/BAM file with Elasticsearch or MongoDB')
    argsdef.add_argument('--infile', required=True,
                        help='Input SAM BAM file to index')
    argsdef.add_argument('--db', default='MongoDB',
                        help="Database: 'Elasticsearch' or 'MongoDB'")
    argsdef.add_argument('--host',
                        help='Elasticsearch or MongoDB server hostname')
    argsdef.add_argument('--port',
                        help="Elasticsearch or MongoDB server port number")
    argsdef.add_argument('--index',
                        help='Name of the Elasticsearch index or MongoDB database')
    argsdef.add_argument('--collect',
                        help='MongoDB collection name')
    args = argsdef.parse_args()
    index_pysam(args.db, args.infile, args.index, args.collect,
                args.host, args.port)
