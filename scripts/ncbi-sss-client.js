/*
   Example Node.js script to submit BLAST sequence similarity searches
   to NCBI compute farms.

   Before running this script install required node.js libraries:
   > npm install node-rest-client fasta-parser minimist querystring fs

   Example command line to run:
   > node ncbi-sss-client.js\
    --qseqsfile=your/query/sequences.fasta\
    --email='your@email'\
    --database='nr'\
    --program='blastp'

BLAST Parameters help (this script expects parameter names in lowercase):
http://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Web&PAGE_TYPE=BlastDocs&DOC_TYPE=BlastHelp#filter

https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Web&PAGE_TYPE=BlastDocs&DOC_TYPE=DeveloperInfo
  1.) Do not contact the server more often than once every three seconds.
  2.) Do not poll for any single RID more often than once a minute.
  3.) Use the URL parameter email, and tool, so that we can track your project
      and contact you if there is a problem.
  4.) Run scripts weekends or between 9 pm and 5 am Eastern Time weekday
      if more than 50 searches will be submitted.

   This script was developed in King Abdullah University of Science and Technology,
   Thuwal, SA.
*/
var Client = require('node-rest-client').Client;
var client = new Client();
var fs = require('fs');
var fasta = require('fasta-parser');
var parser = fasta();
var querystring = require('querystring');
var argv = require('minimist')(process.argv.slice(2));

var url = 'https://blast.ncbi.nlm.nih.gov';
var path = '/blast/Blast.cgi';


function waitJobCompletion(jobid, waittime) {
    console.log("waitJobCompletion: " + jobid);
    setTimeout(function () { status(jobid); }, waittime);
}


function run(args) {
    var req = client.post(url + path, args, function (res) {
        var re = /^    RID = (.*$)/m;
        var l = re.exec(res);
        if(l !== null && l.length > 0 && l[1].length > 0){
            var jobid = l[1];
            console.log('jobid: ' + jobid);
            var rtoe = 60000; // TODO: read from resposnse returned
            waitJobCompletion(jobid, rtoe);
        }
        else {
            console.log("No job id:");
            console.log(res.toString());
        }
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


function getStatusRequest(jobid) {
    var req = "?"
        + 'tool=ncbi-sss-nodesj-client'
        + '&CMD=Get&FORMAT_OBJECT=SearchInfo&RID=' + jobid;
    return req;
}


function status(jobid) {
    var req;
    req = client.get(url + path +  getStatusRequest(jobid), {}, function(res) {
        var r = res.toString();
        console.log('status: ' + jobid);
        if (r.search(/\s+Status=READY/m) != -1) {
            if (r.search(/\s+ThereAreHits=yes/m) != -1)
            {
                console.log("Search complete, retrieving results...\n");
                result(jobid, 'JSON2_S');
            }
            else
            {
                console.log("No hits found.\n");
            }
        }
        else if (r.search(/\s+Status=WAITING/m) != -1) {
            waitJobCompletion(jobid, 60000);
        }
        else if (r.search(/\s+Status=UNKNOWN/m) != -1) {
            console.log('Search ' + jobid + ' expired.');
        }
    });
    req.on('error', function (err) {
        console.log('get status request failed', err);
    });
}


function getResultRequest(jobid, format) {
    var req = "?"
        + 'RESULTS_FILE=on'
        + '&RID=' + jobid
        + '&FORMAT_TYPE=' + format
        + '&CMD=Get&FORMAT_OBJECT=Alignment&RID=' + jobid;
    return req;
}


function result(jobid, resulttype) {
    var rreq = url + path + getResultRequest(jobid, resulttype);
    console.log(rreq);
    var req = client.get(rreq, {}, function (res) {
        var outfile;
        console.log('writing  results for job ' + jobid);
        console.log('writing  results  argv.outfile=' + argv.outfile);
        if (argv.outfile !== undefined)
            outfile = argv.outfile;
        else
            outfile = jobd;
        fs.writeFileSync(outfile + ".json", JSON.stringify(res, null, '\t'));
    });
    req.on('error', function (err) {
        console.log('get result request failed', err);
    });
}


function readInputFastaFileAndSubmitSingleRequest(file) {
    var seq = fs.readFileSync(file, 'utf8');
    console.log(seq.trim());
    var req = getSubmitRequest(seq.trim());
    run(req);
}


// Submit separate request for each sequence in the input file
function readInputFastaFileAndSubmitSeparateRequests(file) {
    b = fs.readFileSync(file, 'utf8');
    i = 0;
    parser.on('data', function (data) {
        if (++i < 2) {
            //console.log(JSON.parse(data.toString()))
            a = JSON.parse(data.toString());
            sid = a.id;
            seq = ">" + a.id + "\n" + a.seq;
            console.log(seq);
            run(getSubmitRequest(seq));
        }
    });
    parser.write(b);
    parser.end();
}


// data for the submit request
function getSubmitRequest(seq) {
    var r = {
        'QUERY': seq,
        'email': argv.email,
        'DATABASE': argv.database,
        'PROGRAM': argv.program,
        'CMD': 'Put'
    };
    
    if(argv.expect !== undefined) r.EXPECT = argv.expect;
    if(argv.hitlist_size !== undefined) r.HITLIST_SIZE = argv.hitlist_size;
    if(argv.alignments !== undefined) r.ALIGNMENTS = argv.alignments;
    if(argv.word_size !== undefined) r.WORD_SIZE = argv.word_size;
    if(argv.filter !== undefined) r.FILTER = argv.filter;
    if(argv.gapcosts !== undefined) r.GAPCOSTS = argv.gapcosts;
    
    var data = querystring.stringify(r);

    var args = {
        data: data,
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': Buffer.byteLength(data)
        }
    };
    return args;
}


if (argv.qseqsfile !== undefined) {
    var qseqsfile = argv.qseqsfile;
    readInputFastaFileAndSubmitSingleRequest(qseqsfile);
    //readInputFastaFileAndSubmitSeparateRequests(qseqsfile);
}
else if (argv.qseqids !== undefined) {
    var qseqids = argv.qseqids;
    qseqids = qseqids.split(" ").join('\n');
    var req = getSubmitRequest(qseqids);
    run(req);
}
 else {
    console.log("Query sequences file or sequence identifiers not specified");
}
