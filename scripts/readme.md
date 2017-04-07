
This folder includes executable scripts of the project
and the index-type mapping files:

* [init-index.sh](): Initialize a new Elasticsearch index with given name
  for indexing BLAST xml2/json results as well as for SAM files

- delete-index.sh:
  Delete specified Elasticsearch index

- delete.sh
  Delete specified BLAST result from specified Elasticsearch index

- ebi-sss-client.sh: Node.js script to submit NCBI-BLAST sequence similarity
  searches to EMBL-EBI compute farms
