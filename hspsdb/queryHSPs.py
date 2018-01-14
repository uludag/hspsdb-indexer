#!/usr/bin/env python
""" Query indexed HSPs data, save results in PivotTable.js files """

import json
import argh
from argh import arg

import pandas as pd
from nosqlbiosets.dbutils import DBconnection
from nosqlbiosets.uniprot.query import QueryUniProt
from pivottablejs import pivot_ui

INDEX = "biosets"
qryuniprot = QueryUniProt("MongoDB", INDEX, "uniprot")
mdbc = DBconnection("MongoDB", INDEX)


class QueryHSPs():

    def _topmatches_linked2UniProt_genes_GO(self, collection,
                                            bitscore=128,
                                            mismatch=1, limit=100):
        qc = {"bitscore": {"$gt": bitscore},
              "mismatch": {"$lt": mismatch}
              }
        aggqc = [
            {"$match": qc},
            {"$lookup": {
                "from": 'uniprot',
                "localField": "sseqid",
                "foreignField": "_id",
                "as": "uniprot"
            }},
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
                    "feattype": {"$arrayElemAt": [
                        "$uniprot.dbReference.property", 0]},
                    "feature": "$uniprot.gene.name.#text"
                },
                "total": {"$sum": 1}}
            },
            {"$sort": {"total": -1}},
            {"$limit": limit}
        ]
        r = mdbc.mdbi[collection].aggregate(aggqc)
        return r

    def topmatches_linked2UniProt_genes_GO(self, collection, outfile,
                                           bitscore=100,
                                           mismatch=1, limit=600):
        r = self._topmatches_linked2UniProt_genes_GO(collection,
                                                     bitscore=bitscore,
                                                     mismatch=mismatch,
                                                     limit=limit)
        rr = []
        for i in r:
            goterm = i['_id']['feattype']['value'][2:]
            goclass = i['_id']['feattype']['value'][:1]
            if goclass == 'C':
                goclass = 'Cellular component'
            elif goclass == 'P':
                goclass = 'Biological process'
            else:
                goclass = 'Molecular function'
            sample = i['_id']['sample']
            feat = i['_id']['feature']
            total = i['total']
            rr.append((sample, goclass, goterm, feat, total))
        print(json.dump(rr, open(outfile+'.json', 'w'), indent=4))
        df = pd.DataFrame(rr,
                          columns=['Sample', 'GO group', 'GO term',
                                   'Gene', 'Abundance'])
        pivot_ui(df, outfile_path=outfile+'.html',
                 rows=['GO group', 'GO term', 'Gene'],
                 cols=['Sample'],
                 rendererName="Heatmap", aggregatorName="Sum",
                 vals=["Abundance"])


@arg('collection', help='Name of the MongoDB collection for HSPs of a study')
@arg('outfile', help='File name for the pivot table to be generated')
def topgenes(collection, outfile, bitscore=100, mismatch=1, limit=600):
    qry = QueryHSPs()
    qry.topmatches_linked2UniProt_genes_GO(collection, outfile,
                                           bitscore, mismatch, limit)

if __name__ == "__main__":
    argh.dispatch_commands([
        topgenespivot
    ])
