#!/usr/bin/env python
""" Query MongoDB indexed HSPs, save results in PivotTable.js html files.
 Current version supports search results against UniProt sequences only
 """
from __future__ import division
import json

import argh
import pandas as pd
from argh import arg
from nosqlbiosets.dbutils import DBconnection
from nosqlbiosets.uniprot.query import QueryUniProt
from pivottablejs import pivot_ui
import logging


INDEX = "biosets"
qryuniprot = QueryUniProt("MongoDB", INDEX, "uniprot")
mdbc = DBconnection("MongoDB", INDEX)
log = logging.getLogger(__name__)

class QueryHSPs():

    def _topmatches_qc(self, bitscore, mismatch):
        qc = {"bitscore": {"$gte": bitscore},
              "mismatch": {"$lte": mismatch}
              }
        return qc

    # Check whether HSP ids are UniProt names or accessions
    def _is_id_name(self, collection):
        r = mdbc.mdbi[collection].find({}, limit=1)
        r = list(r)
        assert 1 == len(r)
        id = r[0]['sseqid']
        return True if '_' in id else False


    def _topmatches_linked2uniprot_qc(self, collection, bitscore, mismatch):
        qc = self._topmatches_qc(bitscore, mismatch)
        lookupfield = '_id' if self._is_id_name(collection) else 'accession'
        aggqc = [
            {"$match": qc},
            {"$lookup": {
                "from": 'uniprot',
                "localField": "sseqid",
                "foreignField": lookupfield,
                "as": "uniprot"
            }}
        ]
        return aggqc

    def topmatches_linked2UniProt(self, collection, bitscore,
                                  mismatch, limit):
        aggqc = self._topmatches_linked2uniprot_qc(collection, bitscore,
                                                   mismatch)
        aggqc += [
            {"$project": {"uniprot.gene":1, "uniprot.dbReference": 1,
                          "uniprot.organism": 1}},
            {"$unwind": "$uniprot"},
            {"$unwind": "$uniprot.gene"},
            {"$unwind": "$uniprot.gene.name"},
            {"$match": {"uniprot.gene.name.type":
                            {"$in": ["primary"]}}},
            {"$unwind": "$uniprot.dbReference"},
            {"$match": {"uniprot.dbReference.type": {"$in": ['GO']}}},
            {"$group": {
                "_id": {
                    "sample": "$_id.sample",
                    "goannot": {"$arrayElemAt": [
                        "$uniprot.dbReference.property", 0]},
                    "gene": "$uniprot.gene.name.#text",
                    "organism": "$uniprot.organism.name.#text"
                },
                "abundance": {"$sum": 1},
                # TODO: normalized abundance values
                "bitscore": {"$sum": "$bitscore"}
            }},
            {"$sort": {"abundance": -1}},
            {"$limit": limit}
        ]
        cr = mdbc.mdbi[collection].aggregate(aggqc, allowDiskUse=True)
        log.info('topmatches_linked2UniProt query returned')
        r = []
        nsamples = {}
        for i in cr:
            goterm = i['_id']['goannot']['value'][2:]
            goclass = i['_id']['goannot']['value'][:1]
            if goclass == 'C':
                goclass = 'Cellular component'
            elif goclass == 'P':
                goclass = 'Biological process'
            else:
                goclass = 'Molecular function'
            sample = i['_id']['sample']
            gene = i['_id']['gene']
            organism = i['_id']['organism']
            abundance = i['abundance']
            bitscore = i['bitscore']
            r.append((sample, organism, goclass, goterm, gene,
                      abundance, bitscore))
            if sample in nsamples:
                nsamples[sample] += 1
            else:
                nsamples[sample] = 1
        print(nsamples)
        n = sum(nsamples.values())
        r = [row +
             (row[5] * n // nsamples[row[0]],)
             for row in r]
        return r

    @staticmethod
    def save_topmatches_linked2UniProt(r, outfile,
                                       rows=['GO group', 'GO term', 'Gene']):
        json.dump(r, open(outfile+'.json', 'w'), indent=4)
        df = pd.DataFrame(r,
                          columns=['Sample', 'Organism', 'GO group', 'GO term',
                                   'Gene', 'Abundance', 'Bitscore',
                                   'Normalized abundance'])
        if not outfile.endswith('.html'):
            outfile += '.html'
        pivot_ui(df, outfile_path=outfile,
                 rows=rows,
                 cols=['Sample'],
                 rendererName="Heatmap",
                 aggregatorName="Integer Sum",
                 rowOrder='value_z_to_a',
                 vals=["Normalized abundance"])
        print('Pivot table of query results saved in '+ outfile)


@arg('study', help='Name of the MongoDB collection for HSPs of a study')
@arg('outfile', help='Name for the pivot table html file to be generated')
@arg('--bitscore', help='Minimum bitscore of HSPs')
@arg('--mismatch', help='Maximum mismatch in HSPs')
@arg('--limit', help='Maximum number of groups in the aggreagted results')
@arg('--rows', help='Default rows for the output pivot table')
def topgenes(study, outfile, bitscore=100, mismatch=1, limit=14000,
             rows='Gene'):
    """
    Abundance of HSPs grouped by organisms, genes, and GO annotations.
    Query results are saved in a json file and as PivotTable.js html files
    """
    qry = QueryHSPs()
    r = qry.topmatches_linked2UniProt(study, bitscore, mismatch, limit)
    rows = [r.strip() for r in rows.split(",")]
    qry.save_topmatches_linked2UniProt(r, outfile, rows)


if __name__ == "__main__":
    argh.dispatch_commands([
        topgenes
    ])
