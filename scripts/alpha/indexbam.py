#!/usr/bin/env python
""" Index given BAM file with Elasticsearch """
from __future__ import print_function
import json, os
import argparse
from elasticsearch import Elasticsearch
from lib.pybam import pybam


def getcigar(a):
    c = ""
    if len(a) == 0: c = "*"
    for pair in a:
        c += str(pair[1])
        c += pair[0]
    return c


# TODO: we should store reference name indexes rather than names
def read_and_index_bam(infile, es, index):
    parser = ['sam_qname', 'sam_flag', 'sam_refID', 'sam_pos1',
              'sam_mapq', 'sam_cigar_string',
              'sam_next_refID', 'sam_pnext1', 'sam_tlen', 'sam_seq',
              'sam_l_read_name']
    print("Reading input file '%s' for indexing" % infile)
    pure_bam = pybam.read(infile, parser)
    print("Reference sequence names with lengths:")
    print(pure_bam.file_chromosome_lengths)
    i = 1
    for read in pure_bam:
        r = dict()
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
        # TODO: readSequence vs readString(htsjdk library use this name) ?
        r['readString'] = read[9]
        r['filename'] = infile
        es_index_bamr(es, index, r, infile+str(i))
        i += 1


def es_index_bamr(es, index, r, rid):
    r = es.index(index=index, doc_type='sam',
                 id=rid, body=json.dumps(r))
    return r


def initindex_ifnotdefined(es, index):
    # es.indices.delete(index=index, params={"timeout": "10s"})
    if not es.indices.exists(index=index):
        d = os.path.dirname(os.path.abspath(__file__))
        m = json.load(open(d + "/../mappings-sam.json", "r"))
        c = {"settings": {"index": {
                "number_of_shards": "5",
                "number_of_replicas": "0",
                "refresh_interval": -1
            }},
            "mappings": m
            }
        es.indices.create(index=index, params={"timeout": "20s"},
                          ignore=400, body=c)


def main(es, infile, index):
    initindex_ifnotdefined(es, index)
    read_and_index_bam(infile, es, index)
    es.indices.refresh(index=index)


if __name__ == '__main__':
    argsdef = argparse.ArgumentParser(
        description='Index given BAM file with Elasticsearch')
    argsdef.add_argument('--infile',
                        help='Input BAM file to index')
    argsdef.add_argument('--index',
                        default="hspsdb",
                        help='Name of the Elasticsearch index')
    argsdef.add_argument('--host', default="bio2rdf",
                        help='Elasticsearch server hostname')
    argsdef.add_argument('--port', default="9200",
                        help="Elasticsearch server port")
    args = argsdef.parse_args()
    host = args.host
    port = args.port
    con = Elasticsearch(host=host, port=port, timeout=600)
    main(con, args.infile, args.index)
