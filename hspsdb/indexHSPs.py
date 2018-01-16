#!/usr/bin/env python
""" Index tabular sequence similarity search result files """
from __future__ import print_function

from pprint import pprint

import argh
import pandas as pd
from argh import arg
from nosqlbiosets.dbutils import DBconnection
from pymongo.errors import BulkWriteError

CHUNK_SIZE = 2048

names = ["qseqid", "sseqid", "pident", "length", "mismatch",
         "gapopen", "qstart", "qend", "sstart", "send", "evalue", "bitscore"]

''' Default 12 columns: https://github.com/seqan/lambda/wiki/BLAST-Output-Formats
Query Seq-id, Subject Seq-id, Percentage of identical matches, Alignment length,
Number of mismatches, Number of gap openings, Start of alignment in query,
End of alignment in query, Start of alignment in subject,
End of alignment in subject, Expect value, Bit score
'''


def create_indices(mdb, collection):
    indx_fields = ["length", "sseqid", "bitscore", "mismatch"]
    for field in indx_fields:
        r = mdb[collection].create_index(field)
        print(r)


def _index_hsps(mdbi, infile, sampleid, pair, collection, delimiter='\t'):
    dfr = pd.read_csv(infile, sep=delimiter, header=None, names=names,
                      chunksize=CHUNK_SIZE, index_col=False)
    i = 0
    for df in dfr:
        hsps = df.to_dict(orient="records")
        for hsp in hsps:
            i += 1
            # TODO: improve parsing/selection for search sequence ids
            hsp['sseqid'] = hsp['sseqid'].split('|')[-1]
            del hsp['qseqid']  # until we use this information
            hsp['_id'] = {"hsp": i, "sample": sampleid, "pair": pair}
        try:
            mdbi[collection].insert_many(hsps, ordered=False,
                                         bypass_document_validation=True)
        except BulkWriteError as e:
            pprint(e)
            pprint(e.details)
            exit()
        # if i >= 100000:
        #     break


@arg('infile', help='Similarity search results in tabular format')
@arg('sampleid', help='Id of the sample the query sequences were sequenced from')
@arg('collection', help='MongoDB collection,'
                        ' for indexing/collecting HSPs of the study')
def index(infile, sampleid, collection, pair=-1,
          db="MongoDB", database='biosets', delimiter='\t',
          user=None, password=None, host=None, port=None):
    """
    Index similarity search results of a sample
    """
    dbc = DBconnection(db, database, host=host, port=port, user=user,
                       password=password)
    if dbc.db == "MongoDB":
        # Delete previous reads with the same sample/pair ids
        dbc.mdbi[collection].delete_many({
            '_id.sample': sampleid, '_id.pair': pair})
        _index_hsps(dbc.mdbi, infile, sampleid, pair, collection, delimiter)
        create_indices(dbc.mdbi, collection)

if __name__ == "__main__":
    argh.dispatch_commands([
        index
    ])
