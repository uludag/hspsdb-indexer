#!/bin/bash
# Index BLAST json output files in a given folder
#
# Example usage:
# ./scripts/index-folder.sh ./testdb project-a http://localhost:9200/


infolder=${1-'./data'}
index=${2-'hspsdb-test'}
server=${3-'http://localhost:9200'}


function index() {
    infile=$1
    id=$2
    curl -XPUT ${server}/${index}/xml2/${id} -d @${infile};
    curl -XGET "${server}/${index}/_refresh";
}


i=0;
for infile in `ls ${infolder}/*.json`; do
   id=$(basename "$infile" .json)
   echo ${id}
   index $infile $id
   i=$((i + 1));
done

echo;
curl -XGET "${server}/${index}/_refresh";
echo $?;

echo "${i} files have been indexed"
