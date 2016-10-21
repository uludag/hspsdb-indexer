#!/usr/bin/python2
from lib.pybam import pybam
import json
import argparse
from elasticsearch import Elasticsearch


def getcigar(a):
    c = ""
    if len(a) == 0: c = "*"
    for pair in a:
        c += str(pair[1])
        c += pair[0]
    return c


# for better performance, we can store reference name indexes rather than names?
def read_and_index_bam(infile, es, index):
    pure_bam = pybam.bgunzip(infile)
    parser = pybam.compile_parser(['qname', 'flag', 'refID', 'pos',
                                   'mapq',
                                   'cigar',
                                   'next_refID', 'next_pos', 'tlen', 'seq',
                                   'l_read_name'])
    print(pure_bam.chromosome_names)
    print(pure_bam.chromosome_lengths)
    i = 1
    for read in parser(pure_bam):
        r = dict()
        r['readName'] = read[0]
        r['flags'] = read[1]
        r['referenceName'] = pure_bam.chromosome_names[read[2]]
        r['alignmentStart'] = read[3]
        r['mappingQuality'] = read[4]
        r['cigarString'] = getcigar(read[5])
        r['mateReferenceName'] = pure_bam.chromosome_names[read[6]]
        r['mateAlignmentStart'] = read[7]
        r['readLength'] = read[8]
        r['readSequence'] = read[9]
        print("%s %s %s %s" % (read[0], read[1], read[2], read[3]))
        print(json.dumps(r))
        es_index_bamr(es, index, r, infile+str(i))
        i += 1
    pure_bam = pybam.bgunzip(infile)
    parser = pybam.compile_parser(['qname', 'refID', 'pos'])
    for qname,refID,pos in parser(pure_bam):
        print("-- %s %s %s" % (qname,refID,pos))
        if refID < 0: rname = 'Unmapped'
        else:         rname = pure_bam.chromosome_names[refID]
        print (qname, rname, pos)
        break


def es_index_bamr(es, index, r, rid):
    r = es.index(index=index, doc_type='pysam',
                 id=rid, body=json.dumps(r))
    return r


def initindex_ifnotdefined(es, index):
    # es.indices.delete(index=index, params={"timeout": "10s"})
    m = json.load(open("./scripts/mappings-sam.json", "rt"))

    c = {"settings": {"index": {
            "number_of_shards": "2",
            "number_of_replicas": "0",
            "refresh_interval": -1
        }},
        "mappings": {"pysam": {
            "properties": m["sam"]["properties"]
    }}}
    print(" ------ " + json.dumps(c) + " ------ " )

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
                        default="../src/test/"
                                "resources/htsjdk/samtools/compressed.bam",
                        help='input file to index')
    argsdef.add_argument('--index',
                        default="hspsdb-pytests",
                        help='name of the elasticsearch index')
    argsdef.add_argument('--host', default="farna", #TODO
                        help='Elasticsearch server hostname')
    argsdef.add_argument('--port', default="9301", #TODO
                        help="Elasticsearch server port")
    args = argsdef.parse_args()
    host = args.host
    port = args.port
    con = Elasticsearch(host=host, port=port, timeout=600)
    main(con, args.infile, args.index)
