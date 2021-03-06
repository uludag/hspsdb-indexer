#!/bin/sh
# Index given BLAST output files in json format with Elasticsearch
# Example usage:
# ./scripts/index.sh ./rgsearch-1.json rgsearch-1 index-a http://localhost:9200/

if [ $# -lt 1 ]
then
    echo "Usage:  $0 <jsonfile> <id> <index> [server_url]"
else
    infile=$1
    bname=$(basename "$infile" .json)
    id=${2-${bname}}
    index=${3-'hspsdb-test'}
    server=${4-'http://localhost:9200'}

    curl -XPUT ${server}/${index}/xml2/${id} -d @${infile};

    curl -XPOST "${server}/${index}/_refresh";

    echo
    echo "Index call followed by refresh call, both returned"
fi
