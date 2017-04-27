# HSPs-db indexer

This repository includes scripts for Elasticsearch indexing of sequence similarity search
results, either in NCBI-BLAST xml2/json formats or in SAM/BAM formats.

In a separate repository we develop web interfaces for the indexed results,
https://github.com/uludag/hspsdb-webcode. Latest version of the web interface
for xml2/json outputs is used for a small set of sample BLAST results on a
[test server](http://hspsdb-test.herokuapp.com/).


### Installation ###

Following steps describe how to index BLAST result files in xml2/json formats. 
We will extend this section when the index scripts for SAM/BAM files reach
to a level of maturity.

* Install [Elasticsearch](https://www.elastic.co/downloads/elasticsearch)

* Clone this repository

* Choose an Elasticsearch index name for your BLAST results
  and use [init-index.sh](scripts/init-index.sh)
  script to initialize your index

* If you already have your BLAST outputs in json format use
  [index.sh](scripts/index.sh)
  or [index-folder.sh](scripts/index-folder.sh) scripts
  to index your output files.
  If you do not have any BLAST results in json format and if you first want to
  see how HSPs-db is working,
  then you can use the sample results we have in the testdb folder.
  Call [files2index.sh](scripts/files2index.sh) script with argument `./testdb`
  followed by the index name you choose earlier, and the URL of your Elasticsearch
  server.
  If you already have outputs in BLAST archive format you can use
  `blast_formatter` command to regenerate your outputs in json format.
  We want to implement scripts that maps existing XML outputs to json format
  but this has not been done yet

* After you indexed your BLAST results you can install
 [HSPs-db web interface](https://github.com/uludag/hspsdb-webcode)
  for querying and visualizing indexed BLAST results

* For new BLAST searches it is best to produce outputs first in BLAST archive format
  then use `blast_formatter` to generate the outputs you normally read
  and the json output for indexing

* This repository also includes Node.js client scripts for EMBL-EBI and NCBI,
  BLAST services; [ebi-sss-client.js](scripts/ebi-sss-client.js),
  [ncbi-sss-client.js](scripts/ncbi-sss-client.js).
  Modules required by the scripts can be installed
  by running `npm install` from project root folder

## License

Copyright (c)
 [King Abdullah University of Science and Technology](https://www.kaust.edu.sa/),
 Thuwal, SA
 