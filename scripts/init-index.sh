#!/bin/bash
# Initialize Elasticsearch index with given name for indexing BLAST results
# Example usage:
# ./scripts/init-index.sh project-a http://localhost:9200/

if [ $# -lt 1 ]
then
    echo "Usage: $0 <index name for BLAST json output files>"\
         " [Elasticsearch server url, default:http://localhost:9200/]"
    exit;
fi

index=${1-'hspsdb-test'}
server=${2-'http://localhost:9200'}

echo "Deleting existing index with given name, ignore index_not_found_exception";
curl -XDELETE "${server}/${index}/";
curl -XPOST "${server}/${index}/_refresh";
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
type=xml2;
curl -XPUT "${server}/${index}/_mapping/${type}"\
 -d  @./scripts/mappings.json;
type=sam;
curl -XPUT "${server}/${index}/_mapping/${type}"\
 -d  @./scripts/mappings-sam.json;

echo;echo;
curl -XPOST "${server}/${index}/_refresh";

echo;echo;
