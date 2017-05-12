
This folder includes executable scripts of the project
and the Elasticsearch type-mapping files:

* [init-index.sh](): Initialize a new Elasticsearch index with given name
  for indexing BLAST xml/json results as well as for SAM/BAM files

* [files2index.sh](): Index BLAST json output files given in a folder
 with Elasticsearch

- [delete-index.sh]():
  Delete specified Elasticsearch index

- [delete.sh]():
  Delete specified BLAST result from specified Elasticsearch index

- [ebi-sss-client.sh](): Node.js script to submit NCBI-BLAST sequence similarity
  searches to EMBL-EBI compute farms

- [ncbi-sss-client.sh](): Node.js script to submit NCBI-BLAST sequence similarity
  searches to NCBI compute farms
