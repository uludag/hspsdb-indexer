/*
   Example Node.js script to submit NCBI-BLAST sequence similarity searches
   to EMBL-EBI compute farms, input files can include multiple sequences.

   Before running this script install required node.js libraries:
   > npm install node-rest-client fasta-parser minimist querystring fs

   Example command line:
   > node ebi-sss-client.js\
    --qseqsfile=your/query/sequences.fasta\
    --email='your@email'\
    --database='uniref90'\
    --program='blastp'\
    --stype='protein'

   TODO:
   - Support for optional NCBI-BLAST parameters
   - Support for large number of query sequences,
     EBI requires "not to submit jobs in batches of up to 30 at a time
     and to not submit more until the results and processing has completed for these"

   This script was developed at King Abdullah University of Science and Technology
*/
Client = require('node-rest-client').Client;
client = new Client();
fs = require('fs');
fasta = require('fasta-parser');
parser = fasta();
querystring = require('querystring');
// Change url to www.ebi.ac.uk when not testing the script
url = 'http://wwwdev.ebi.ac.uk';
path = '/Tools/services/rest/ncbiblast/';


function waitJobCompletion(jobid) {
    setTimeout(function () { status(jobid); }, 5000);
}


function run(args) {
    var req = client.post(url + path + 'run/', args, function (res) {
        console.log('jobid: ' + res);
        jobid = res;
        waitJobCompletion(jobid);
    });
    req.on('requestTimeout', function (req) {
        console.log('request has expired');
        req.abort();
    });
    req.on('responseTimeout', function (res) {
        console.log('response has expired');
    });
    req.on('error', function (err) {
        console.log('similarity search request failed', err);
    });
}


function status(jobid) {
    var req = client.get(url + path + 'status/' + jobid,
        {}, function (res) {
            var jstatus = res.toString();
            console.log('status: ' + jobid + " -- " + jstatus);
            if (jstatus === "FINISHED")
                result(jobid, 'out');
            else if (jstatus === "RUNNING")
                waitJobCompletion(jobid);
        });
    req.on('error', function (err) {
        console.log('get status request failed', err);
    });
}


//result(jobid, 'out?format=5');
function result(jobid, resulttype) {
    var req = client.get(url + path + 'result/' + jobid + '/' + resulttype,
        {}, function (res) {
            console.log('writing  results for job ' + jobid);
            fs.writeFileSync(jobid, res);
        });
    req.on('error', function (err) {
        console.log('get result request failed', err);
    });
}


function readInputFastaFileAndSubmit(file) {
    var b = fs.readFileSync(file);
    var i = 0;
    parser.on('data', function (data) {
        if (++i < 20) {
            //console.log(JSON.parse(data.toString()))
            a = JSON.parse(data.toString());
            sid = a.id;
            seq = ">" + a.id + "\n" + a.seq;
            console.log(seq);
            run(getPostData(seq));
        }
    });
    parser.write(b);
    parser.end();
}


// data for the run request
function getPostData(seq) {
    var data = querystring.stringify({
        'sequence': seq,
        'email': argv.email,
        'database': argv.database,
        'program': argv.program,
        'stype': argv.stype
    });
    var args = {
        data: data,
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': Buffer.byteLength(data)
        }
    };
    return args;
}


var argv = require('minimist')(process.argv.slice(2));

if (argv.qseqsfile !== undefined) {
    qseqsfile = argv.qseqsfile;
    readInputFastaFileAndSubmit(qseqsfile);
} else {
    console.log("No query sequences file specified");
}
