#!/usr/bin/env python
""" Index given BAM file with Elasticsearch """
from __future__ import print_function
import json, os
import argparse
from elasticsearch import Elasticsearch
from pybam import pybam
from elasticsearch.helpers import streaming_bulk

ChunkSize = 2*1024

def getcigar(a):
    c = ""
    if len(a) == 0: c = "*"
    for pair in a:
        c += str(pair[1])
        c += pair[0]
    return c


# TODO: we should store reference name indexes rather than names
class BAMReader:

    def __init__(self, infile):
        self.infile = infile
        self.i = 0

    def read_bam(self):
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
            r['filename'] = self.infile
            r['_id'] = self.infile + str(self.i)
            yield r


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
        r = es.indices.create(index=index, params={"timeout": "20s"},
                              # ignore=400,
                              body=c)
        print(r)


# TODO: parallel_bulk
def index(infile, index, host=None, port=None):
    conf = {"es_host": "localhost", "es_port": 9200}
    d = os.path.dirname(os.path.abspath(__file__))
    try:
        conf = json.load(open(d + "/../../conf/elasticsearch.json", "r"))
    finally:
        pass
    if host is None:
        host = conf['es_host']
    if port is None:
        port = conf['es_port']
    esc = Elasticsearch(host=host, port=port, timeout=600)
    initindex_ifnotdefined(esc, index)
    i = BAMReader(infile)
    for ok, result in streaming_bulk(
            esc,
            i.read_bam(),
            index=index,
            doc_type='sam',
            chunk_size=ChunkSize
    ):
        action, result = result.popitem()
        doc_id = '/%s/commits/%s' % (index, result['_id'])
        if not ok:
            print('Failed to %s document %s: %r' % (action, doc_id, result))
    esc.indices.refresh(index=index)
    return i.i


if __name__ == '__main__':
    argsdef = argparse.ArgumentParser(
        description='Index given BAM file with Elasticsearch')
    argsdef.add_argument('--infile', required=True,
                        help='Input BAM file to index')
    argsdef.add_argument('--index',
                        default="hspsdb",
                        help='Name of the Elasticsearch index')
    argsdef.add_argument('--host',
                        help='Elasticsearch server hostname')
    argsdef.add_argument('--port',
                        help="Elasticsearch server port")
    args = argsdef.parse_args()
    index(args.infile, args.index, args.host, args.port)
