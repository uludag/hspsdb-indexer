#!/usr/bin/env python
""" Query indexed HSPs data, save results in PivotTable.js files """

import json

import argh
import pandas as pd
from argh import arg
from nosqlbiosets.dbutils import DBconnection
from nosqlbiosets.uniprot.query import QueryUniProt
from pivottablejs import pivot_ui

INDEX = "biosets"
qryuniprot = QueryUniProt("MongoDB", INDEX, "uniprot")
mdbc = DBconnection("MongoDB", INDEX)


class QueryHSPs():

    def _topmatches_qc(self, bitscore=128, mismatch=1):
        qc = {"bitscore": {"$gt": bitscore},
              "mismatch": {"$lt": mismatch}
              }
        return qc

    def _topmatches_linked2uniprot_qc(self, bitscore=128, mismatch=1):
        qc = self._topmatches_qc(bitscore, mismatch)
        aggqc = [
            {"$match": qc},
            {"$lookup": {
                "from": 'uniprot',
                "localField": "sseqid",
                "foreignField": "_id",
                "as": "uniprot"
            }}
        ]
        return aggqc

    def topmatches_linked2UniProt(self, collection,
                                  bitscore=128, mismatch=1,
                                  limit=100):
        aggqc = self._topmatches_linked2uniprot_qc(bitscore, mismatch)
        aggqc += [
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
                "bitscore": {"$sum": "$bitscore"}
            }},
            {"$sort": {"abundance": -1}},
            {"$limit": limit}
        ]
        cr = mdbc.mdbi[collection].aggregate(aggqc)
        r = []
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
        return r

    @staticmethod
    def save_topmatches_linked2UniProt(r, outfile):
        json.dump(r, open(outfile+'.json', 'w'), indent=4)
        df = pd.DataFrame(r,
                          columns=['Sample', 'Organism', 'GO group', 'GO term',
                                   'Gene', 'Abundance', 'Bitscore'])
        pivot_ui(df, outfile_path=outfile+'.html',
                 rows=['GO group', 'GO term', 'Gene'],
                 cols=['Sample'],
                 rendererName="Heatmap", aggregatorName="Sum",
                 vals=["Abundance"])


@arg('study', help='Name of the MongoDB collection for HSPs of a study')
@arg('outfile', help='File name for the pivot table to be generated')
@arg('--bitscore', help='Minimum bitscore of HSPs')
@arg('--mismatch', help='Maximum mismatch in HSPs')
def topgenes(study, outfile, bitscore=100, mismatch=1, limit=600):
    """
    Abundance of HSPs grouped by organisms, genes, and GO annotations.
    Query results are saved in a json file and as PivotTable.js html file
    """
    qry = QueryHSPs()
    r = qry.topmatches_linked2UniProt(study, bitscore, mismatch, limit)
    qry.save_topmatches_linked2UniProt(r, outfile)


if __name__ == "__main__":
    argh.dispatch_commands([
        topgenes
    ])
