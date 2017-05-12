#!/usr/bin/env python
""" Index given BLAST json output file with Elasticsearch """
import argparse
import json
import os

from elasticsearch import Elasticsearch


# Read BLAST json output file and index with Elasticsearch
def read_index_jsonfile(es, infile, index, docid):
    print("Read %s " % infile)
    f = open(infile, 'r')
    doc = json.load(f)
    ret = es.index(index=index,
                   doc_type='xml2',
                   id=docid,
                   body=doc)
    print("... indexed = %s" % ret['created'])
    return


def initindex_ifnotdefined(es, index):
    # es.indices.delete(index=index, params={"timeout": "10s"})
    if not es.indices.exists(index=index):
        d = os.path.dirname(os.path.abspath(__file__))
        m = json.load(open(d + "/mappings.json", "r"))
        c = {"settings": {"index": {
                "number_of_shards": "5",
                "number_of_replicas": "0",
                "refresh_interval": -1
            }},
            "mappings": m
            }
        es.indices.create(index=index, params={"timeout": "20s"},
                          ignore=400, body=c)

def main(es, infile, index, docid):
    initindex_ifnotdefined(es, index)
    read_index_jsonfile(es, infile, index, docid)
    es.indices.refresh(index=index)


if __name__ == '__main__':
    conf = {"host": "localhost", "port": 9200}
    d = os.path.dirname(os.path.abspath(__file__))
    try:
        conf = json.load(open(d + "/../conf/elasticsearch.json", "r"))
    finally:
        pass
    argsdef = argparse.ArgumentParser(
        description='Index given BAM file with Elasticsearch')
    argsdef.add_argument('--infile',
                         default="../testdb/uniprot_search1.json",
                         help='BLAST json output file to index')
    argsdef.add_argument('--id',
                         help='Elasticsearch doc id (default is file-name)')
    argsdef.add_argument('--index',
                         default="hspsdb",
                         help='Name of the Elasticsearch index')
    argsdef.add_argument('--host', default="localhost",
                         help='Elasticsearch server hostname')
    argsdef.add_argument('--port', default="9200",
                         help="Elasticsearch server port")
    args = argsdef.parse_args()
    es = Elasticsearch(host=args.host, port=args.port, timeout=600)
    if args.id is None:
        docid = args.infile
    else:
        docid = args.id
    main(es, args.infile, args.index, docid)
