# HSPs-db

HSPs-db project aims developing tools for indexing NCBI BLAST
search results, together with data mining interfaces.

Everyday researchers all over the world run millions of NCBI BLAST sequence
similarity searches; aim here is to prepare tools to make more sense of these
search results.
Latest version of the NCBI-BLAST software have improved outputs (xml2 project)
which makes our task easier.

We use Elasticsearch for indexing and storing BLAST results.
We have open eye for Solr and Mongodb.
         
### What is this repository for? ###

You run many NCBI-BLAST searches and want to be able to query all your results
from a data-mining web interface that should allow you see the correlations across
your results, and select subsets easily for further analysis.

### How do I get set up? ###

* Install Elasticsearch or have a cloud provided service (e.g. see Red Hat Cloud services)

* Clone this repository

* Choose an Elasticsearch index name for your BLAST results and use `init-index.sh` script, in
  scripts folder to initialize your index

* If you already have your BLAST outputs in json format use `index.sh`
  or `index-folder.sh` scripts we have to index your results

* If you do not have any BLAST results in json format and if you first want to
  see how HSPs-db is working then you can use the sample results we
  have in the testdb folder. Call `index-folder.sh` script with argument `./testdb`
  followed by the index name you choose earlier and your Elasticsearch server URL

* If you already have outputs in BLAST archive format you can use
  `blast_formatter` command to regenerate your outputs in json format

* We want to have scripts that maps existing XML outputs to json format
  but this has not been done yet

* For your new BLAST jobs it is best to produce outputs first in BLAST archive format
  then use `blast_formatter` to generate the outputs you normally read
  and the json output for indexing


## License

Copyright (c) King Abdullah University of Science and Technology, Thuwal, SA
