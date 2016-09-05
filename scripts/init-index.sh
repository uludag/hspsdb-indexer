#!/bin/bash

# Initialize Elasticsearch index with given name
# for indexing/storing BLAST results
# Example usage:
# ./scripts/init-index.sh project-a http://localhost:9200/


type=xml2;
index=${1-'hspsdb-test'}
server=${2-'http://localhost:9200'}

echo "Deleting existing index with same name, ignore index_not_found_exception";
curl -XDELETE "${server}/${index}/";
curl -XGET "${server}/${index}/_refresh";
echo;echo;
curl -XPUT "${server}/${index}/" -d '
{
    "settings" : {
        "number_of_shards" : 1,
        "number_of_replicas" : 0,
        "index.refresh_interval": "-1"
    }
}';

echo;echo;

curl -XPUT "${server}/${index}/_mapping/${type}"\
 -d  @./scripts/mappings.json;

echo;echo;
curl -XGET "${server}/${index}/_refresh";

echo;echo;
