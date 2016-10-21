#!/bin/bash
# Elasticsearch index BLAST json output files in a given folder
#
# Example usage:
# ./scripts/files2index.sh ./testdb index-a http://localhost:9200/


infolder=${1-'./testdb'}
index=${2-'hspsdb-test'}
server=${3-'http://localhost:9200'}


function index() {
    infile=$1
    id=$2
    curl -XPUT ${server}/${index}/xml2/${id} -d @${infile};
}

if [ $# -lt 1 ]
then
    echo "Usage: $0 <folder with BLAST json output files> <index name> [server url]"
else
    i=0;
    for infile in `ls ${infolder}/*.json`; do
        id=$(basename "$infile" .json)
        echo ${id}
        index $infile $id
        i=$((i + 1));
    done

    echo;
    curl -XPOST "${server}/${index}/_refresh";
    echo $?;

    echo "${i} files have been indexed";
fi
