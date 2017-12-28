#!/usr/bin/env python
""" Index tabular sequence similarity search result files """
from __future__ import print_function

import os
from pprint import pprint

import pandas as pd
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
    indx_fields = ["length", "sseqid"]
    for field in indx_fields:
        mdb[collection].create_index(field)


def index_hsps(mdbi, infile, sampleid, pair, collection, delimiter='\t'):
    dfr = pd.read_csv(infile, sep=delimiter, header=None, names=names,
                      chunksize=CHUNK_SIZE, index_col=False)
    i = 0
    for df in dfr:
        hsps = df.to_dict(orient="records")
        for hsp in hsps:
            i += 1
            hsp['_id'] = {"read": i, "sample": sampleid, "pair": pair}
        try:
            mdbi[collection].insert_many(hsps, ordered=False,
                                         bypass_document_validation=True)
        except BulkWriteError as e:
            pprint(e)
            pprint(e.details)
            exit()
        if i >= CHUNK_SIZE * 10:
            break

def main(db, infile, sampleid, pair, index, collection, delimiter='\t',
         user=None, password=None, host=None, port=None):
    dbc = DBconnection(db, index, host=host, port=port, user=user,
                       password=password)
    if dbc.db == "MongoDB":
        # Delete previous reads with the same sample-id and pair-id
        dbc.mdbi[collection].delete_many({
            '_id.sample': sampleid, '_id.pair': pair})
        index_hsps(dbc.mdbi, infile, sampleid, pair, collection, delimiter)
        create_indices(dbc.mdbi, collection)
