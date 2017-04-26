#!/usr/bin/env python
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


# for better performance, we can store reference name indexes rather than names?
def read_and_index_bam(infile, es, index):
    parser = ['sam_qname', 'sam_flag', 'sam_refID', 'sam_pos1',
              'sam_mapq',
              'sam_cigar_string',
              'sam_next_refID', 'sam_pnext1', 'sam_tlen', 'sam_seq',
              'sam_l_read_name']
    print(infile)
    pure_bam = pybam.read(infile, parser)
    print(pure_bam.file_chromosomes)
    print(pure_bam.file_chromosome_lengths)
    i = 1
    for read in pure_bam:
        r = dict()
        r['readName'] = read[0]
        r['flags'] = read[1]
        refid = read[2]
        if refid < 0:
            rname = 'Unmapped'
            print(rname)
        else:
            r['referenceName'] = pure_bam.file_chromosomes[refid]
        r['alignmentStart'] = read[3]
        r['mappingQuality'] = read[4]
        r['cigarString'] = read[5]
        r['mateReferenceName'] = pure_bam.file_chromosomes[read[6]]
        r['mateAlignmentStart'] = read[7]
        r['readLength'] = read[8]
        r['readSequence'] = read[9]
        print("%s %s %s %s" % (read[0], read[1], read[2], read[3]))
        print(json.dumps(r))
        es_index_bamr(es, index, r, infile+str(i))
        i += 1


def es_index_bamr(es, index, r, rid):
    r = es.index(index=index, doc_type='pysam',
                 id=rid, body=json.dumps(r))
    return r


def initindex_ifnotdefined(es, index):
    # es.indices.delete(index=index, params={"timeout": "10s"})
    d = os.path.dirname(os.path.abspath(__file__))
    m = json.load(open(d + "/../mappings-sam.json", "r"))

    c = {"settings": {"index": {
            "number_of_shards": "5",
            "number_of_replicas": "0",
            "refresh_interval": -1
        }},
        "mappings": {"pysam": m["sam"]
        }}

    es.indices.create(index=index, params={"timeout": "20s"},
                      ignore=400, body=c)


def main(es, infile, index):
    initindex_ifnotdefined(es, index)
    read_and_index_bam(infile, es, index)
    es.indices.refresh(index=index)


if __name__ == '__main__':
    argsdef = argparse.ArgumentParser(
        description='Index Given BAM file, using Elasticsearch')
    argsdef.add_argument('--infile',
                        default="../../src/test/"
                                "resources/htsjdk/samtools/compressed.bam",
                        help='input file to index')
    argsdef.add_argument('--index',
                        default="hspsdb-pytests",
                        help='name of the elasticsearch index')
    argsdef.add_argument('--host', default="bio2rdf", # TODO: config files
                        help='Elasticsearch server hostname')
    argsdef.add_argument('--port', default="9200", # TODO: config files
                        help="Elasticsearch server port")
    args = argsdef.parse_args()
    host = args.host
    port = args.port
    con = Elasticsearch(host=host, port=port, timeout=600)
    main(con, args.infile, args.index)
