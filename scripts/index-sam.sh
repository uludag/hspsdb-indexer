#!/bin/sh

infile=$1
index=${2-'hspsdb'}
server=${3-'http://localhost:9200'}

function print_usage()
 {
    echo "Index given sequence similarity search results file (in SAM format)"
    echo "Requires Java and Maven installed"
    echo ""
    echo "Usage:  $0 <samfile> [<index> [<server>]] "
    echo ""
    echo "server: Elasticsearch server"
    echo "id: Elasticsearch database id for the new record"
    echo ""
}

if [ $# -lt 1 ]
then
    print_usage;
else
    echo "${infile} ${index} ${server}"

    mvn exec:java -Dexec.mainClass=sa.edu.kaust.hspsdb.SAMFileIndexer\
     -Dexec.args="${infile} ${index} ${server}";

    echo;

    curl -XPOST "${server}/${index}/_refresh";

    echo $?;
fi
