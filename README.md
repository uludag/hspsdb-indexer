# HSPs-db indexer

This repository includes small set of scripts for indexing NCBI BLAST sequence
similarity search output files using Elasticsearch.


### Installation ###

* Install [Elasticsearch](https://www.elastic.co/downloads/elasticsearch).
  If you are new to Elasticsearch you may find Elasticsearch [kopf]
  (https://github.com/lmenezes/elasticsearch-kopf) plugin useful
  to understand and admin your server

* Clone this repository

* Choose an Elasticsearch index name for your BLAST results
  and use [init-index.sh](blob/master/scripts/index-init.sh)
  script to initialize your index

* If you already have your BLAST outputs in json format use [index.sh]
  (blob/master/scripts/index.sh)
  or [index-folder.sh](blob/master/scripts/index-folder.sh) scripts
  to index your output files

  If you do not have any BLAST results in json format and if you first want to
  see how HSPs-db is working then you can use the sample results we
  have in the testdb folder. Call [index-folder.sh]
  (blob/master/scripts/index-folder.sh) script with argument `./testdb`
  followed by the index name you choose earlier, and URL of your Elasticsearch server

  If you already have outputs in BLAST archive format you can use
  `blast_formatter` command to regenerate your outputs in json format.
  We want to implement scripts that maps existing XML outputs to json format
  but this has not been done yet

* After you indexed your BLAST results you can install [HSPs-db web interface]
  (https://github.com/uludag/hspsdb-webcode)
  for querying and visualizing indexed BLAST results

* For new BLAST searches it is best to produce outputs first in BLAST archive format
  then use `blast_formatter` to generate the outputs you normally read
  and the json output for indexing

* This project also hosts a Node.js client script for NCBI BLAST service,
  `ncbi-sss-client.js`. Modules required by the script can be installed
  by running `npm install` from project root folder

## License

Copyright (c) King Abdullah University of Science and Technology, Thuwal, SA
