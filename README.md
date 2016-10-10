# HSPs-db indexer

This repository hosts scripts and a Java project
for Elasticsearch indexing of NCBI BLAST sequence similarity search
results, in json and SAM formats.
We have started working on SAM output files only recently;
we do not yet have web interface support for the indexed SAM outputs as we have
for the indexed json outputs; https://github.com/uludag/hspsdb-webcode.
You can see development version of the web interface from the [test server](http://hspsdb-test.herokuapp.com/) we have which is connected to an Elasticsearch server with a small set of sample BLAST results.

[ ![Codeship Status for uludag/hspsdb-indexer]
(https://app.codeship.com/projects/1a5a9020-4dd9-0134-d04d-069048840640/status?branch=master)](https://app.codeship.com/projects/170651)

### Installation ###

* Install [Elasticsearch](https://www.elastic.co/downloads/elasticsearch).
  If you are new to Elasticsearch you may find Elasticsearch
  [kopf](https://github.com/lmenezes/elasticsearch-kopf) plugin useful
  to understand and admin your server

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
  Call [index-folder.sh](scripts/index-folder.sh) script with argument `./testdb`
  followed by the index name you choose earlier, and URL of your Elasticsearch
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