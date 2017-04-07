#!/bin/bash
# Initialize Elasticsearch index with given name
# for indexing sequence similarity search results
# both in BLAST xml2 format and in widely used SAM format
# Example usage:
# ./scripts/init-index.sh hspsdb http://localhost:9200/
# If your Elasticsearch server requires username and password to connect
# then provide them as the 3rd option, e.g. [--user foo:bar]

if [ $# -lt 1 ]
then
    echo "Usage: $0 <index name for BLAST json output files>"\
         " [Elasticsearch server url, default:http://localhost:9200/]"
    exit;
fi

index=${1-'hspsdb-test'}
server=${2-'http://localhost:9200'}
usernamepasswd=${3-'--user elastic:changeme'}

echo "Deleting any existing index with name '${index}', ignore index_not_found_exception";
curl -XDELETE "${server}/${index}/" ${usernamepasswd};
echo;
echo "Refreshing indicies";
curl -XPOST "${server}/_refresh" ${usernamepasswd};
echo;
echo "Initializing new index with name '${index}'";
curl -XPUT "${server}/${index}/" ${usernamepasswd} -d '
{
    "settings" : {
        "number_of_shards" : 1,
        "number_of_replicas" : 0,
        "index.refresh_interval": "-1"
    }
}';

es_5=`curl ${server} ${usernamepasswd} 2>1 | grep 'number" : "5' | wc -l`

if [ "$es_5" = "1" ]; then
    xml2mappings="./scripts/mappings-es5.json"
else
    xml2mappings="./scripts/mappings.json"
fi

echo;
echo "Setting index type mappings";
type=xml2;
curl -XPUT "${server}/${index}/_mapping/${type}" ${usernamepasswd}\
 -d  @${xml2mappings};
type=sam;
curl -XPUT "${server}/${index}/_mapping/${type}" ${usernamepasswd}\
 -d  @./scripts/mappings-sam.json;

echo;
echo "Refreshing indicies";
curl -XPOST "${server}/${index}/_refresh" ${usernamepasswd};

echo;echo;
