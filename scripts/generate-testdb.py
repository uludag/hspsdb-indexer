#!/usr/bin/python3
# Generate sample outputs by submitting BLAST searches to NCBI servers
# and index the results on the given Elasticsearch server.
#
# Set your email address and Elasticsearch server URL
# using the configuration-variables before calling this script.
#
# Make sure you have Node.js installed
# and you executed 'npm install' from project root folder.
#
# Call this script from project root folder, it executes 2 scripts
# from the scripts folder and assumes it was executed from project root folder.
# Do not forget to initialize your Elasticsearch index before running this script, see README

import os

# Configuration variables
qseqids = ["sp|P05067|A4_HUMAN", "sp|P10636|TAU_HUMAN"]
index = 'testdb'
email = 'email@required.for.NCBI.search'
server = 'http://localhost:9200'
outfolder = './testdb'


def submit_search(qseqids, email, database, program, outfile):
    cmd = "node ./scripts/ncbi-sss-client.js --qseqids='{0}'" \
          " --email='{1}'" \
          " --database='{2}'" \
          " --program='{3}'" \
          " --expect=1" \
          " --hitlist_size=10" \
          " --alignments=10" \
          " --word_size=6" \
          " --filter=L" \
          " --gapcosts='11 2'" \
          " --outfile={4}/{5}"
    cmd = cmd.format(qseqids, email, database, program, outfolder, outfile)
    print('BLAST search: ' + cmd)
    os.system(cmd)
    print('BLAST search returned')


def index_resultfile(outfile, id):
    cmd = "./scripts/index.sh {0}/{1}.json {2} {3} {4}"
    cmd = cmd.format(outfolder, outfile, id, index, server)
    os.system(cmd)
    print('index call returned: ' + cmd)


def search_then_index(qseqids, email, database, program, outfile):
    i = 0
    for qseqid in qseqids:
        i += 1
        outf = outfile + str(i)
        submit_search(qseqid, email, database, program, outf)
        index_resultfile(outf, outf)


# Search PDB protein database
search_then_index(qseqids, email, 'pdbaa', 'blastp', 'pdbaa_search')
exit()

# Search Proteins from WGS metagenomic projects using blastp
search_then_index(qseqids, email, 'env_nr', 'blastp', 'env_nr_search')

# Since queries are from swissprot this may not be a good search
# Search Uniprot KB using blastp
search_then_index(qseqids, email, 'swissprot', 'blastp', 'uniprot_search')

# Search refseq_representative_genomes using tblastn
search_then_index(qseqids, email, 'refseq_representative_genomes',
                  'tblastn', 'rg_search')

# Search unfinished High Throughput Genomic Sequences; phases 0, 1 and 2
search_then_index(qseqids, email, 'htgs', 'tblastn', 'htgs_search')
