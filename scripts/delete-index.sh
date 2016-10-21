#!/bin/bash

# Delete Elasticsearch index with given name
# for indexing/storing BLAST results
# Example usage:
# ./scripts/delete-index.sh project-a http://localhost:9200/

index=${1-'hspsdb-test'}
server=${2-'http://localhost:9200'}

curl -XDELETE "${server}/${index}/";

echo;echo;
echo "Delete call returned now making refresh call, ignore index_not_found_exception";

curl -XPOST "${server}/${index}/_refresh";

echo;echo;
echo "Refresh call returned";
