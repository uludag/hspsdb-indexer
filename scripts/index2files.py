#!/usr/bin/python3
# Download BLAST outputs from specified Elasticsearch index
# to the individual json files in a specified folder

import os
import json
from elasticsearch import Elasticsearch, helpers
import argparse


def save(boutput, docid, dest):
    outfile = dest + "/" + docid + ".json"
    print(outfile)
    with open(outfile, 'w') as f:
        f.write(json.dumps(boutput, indent=True))
        f.close()

    return None


def process_all_entries_scan(con, index, dest):
    query = {
        "query": {
            "match_all": {}
        },
        # it is possible to filter the downloaded results using filter queries
        "filter": { "not": {
            "nested": {
                "path": "BlastOutput2.report.results.search.hits.hsps",
                "query": {
                    "match_phrase": {
                        "BlastOutput2.report.results.search.hits.hsps.taxid": "??"
                    }}}}
        }
    }
    ret = helpers.\
        scan(con,
             index=index,
             doc_type="xml2", # Only download classic outputs, not SAM mappings
             scroll="900m",   # 15 h
             query=query
             )
    n = 0
    for doc in ret:
        boutput = doc["_source"]
        save(boutput, doc["_id"], dest)
        n += 1

    return n


def main(con, index, dest):
    if not os.path.isdir(dest):
        os.makedirs(dest)

    n = process_all_entries_scan(con, index,dest)
    print("# of records processed: %d" % n)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Download BLAST output files from given Elasticsearch index')
    parser.add_argument('--index', default="hspsdb-tests",
                        help='Name of the Elasticsearch index')
    parser.add_argument('--host', default="farna",
                        help='Elasticsearch server hostname')
    parser.add_argument('--port', default="9200",
                        help="Elasticsearch server port")
    parser.add_argument('--dest', default="./tmp2",
                        help='Folder to save BLAST output files')
    args = parser.parse_args()
    index = args.index
    host = args.host
    port = args.port
    dest = args.dest

    con = Elasticsearch(host=host, port=port, timeout=120)
    main(con, index, dest)
