#!/bin/sh
# Delete given BLAST result from given Elasticsearch index
# Example usage:
# ./scripts/delete.sh search-1 project-a http://localhost:9200/

if [ $# -lt 1 ]
then
    echo "Usage:  $0 <id> <index> [server_url]"
else
    id=$1
    index=${2-'hspsdb-test'}
    server=${3-'http://localhost:9200'}

    curl -XDELETE ${server}/${index}/xml2/${id};

    curl -XPOST "${server}/${index}/_refresh";

    echo
    echo "Delete call followed by refresh call, both returned"
fi