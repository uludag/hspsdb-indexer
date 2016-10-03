#!/bin/sh

infile=$1
index=${2-'hspsdb-test'}
server=${3-'http://localhost:9200'}

function print_usage()
 {
    echo "Index given SAM sequence similarity search results file"
    echo ""
    echo "Usage:  $0 <samfile> [<index> [<server>]] "
    echo ""
    echo "server: elasticsearch server"
    echo "id: elasticsearch database id for the new record"
    echo ""
}

echo "${infile} ${index} ${server}"

mvn exec:java -Dexec.mainClass=sa.edu.kaust.hspsdb.SAMFileIndexer\
 -Dexec.args="${infile} ${index} ${server}";

echo;

curl -XGET "${server}/${index}/_refresh";

echo $?;


curl -XPUT ${server}/${index}/xml2/${id} -d @${infile};

curl -XGET "${server}/${index}/_refresh";
