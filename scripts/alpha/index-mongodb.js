#!/usr/bin/env node
// Some incomplete work with Nodejs and Mongodb
// (index given BLAST json result files with Mongodb)


var fs = require('fs');
var MongoClient = require('mongodb').MongoClient
var assert = require('assert');
var argv = require('minimist')(process.argv.slice(2));
console.dir(argv);
// Connection URL
var url = 'mongodb://localhost:27017/hspsdb';


var findDocuments = function (db, qterm, callback) {
    var collection = db.collection('xml2');
    var a = collection.find(
        {
            "BlastOutput2.report.program": "blastp",
//            $text: { $search: qterm }
// Command line to generate text indices:
// mongo hspsdb  ./mongodb-index-tests.sh (which should have the following content)
// db.xml2.createIndex({"$**": "text"}, {name: "textindex"});
        }
    ).toArray(function (err, docs) {
        assert.equal(err, null);
        console.log("Found the following records");
        console.dir(docs);
        docs.forEach(function (e, i) {
            var report;
            if (!Array.isArray(e.BlastOutput2))
                report = e.BlastOutput2.report;
            else if (e.BlastOutput2.length > 0)
                report = e.BlastOutput2[0].report; //todo: array processing
            console.log(i + " -- " + report.program);
        });
        callback(docs);//packageResults()
    });
};

// Returns query results in the form similar to Elasticsearch results
// How to refer in other files?:
//   var mdb = require('./mongodb.js');
//   mdb.querymongodb(qterm);
exports.querymongodb = function (qterm) {
    MongoClient.connect(url, function (err, db) {
        if (err === null) {
            console.log("MongoDB querying term: " + qterm);
            findDocuments(db, qterm, function packageResults(qresult) {
                db.close();
                var ret = {
                    hits: {
                        hits: qresult,
                        //TODO: partial results
                        total: qresult.length
                    },
                    aggregations:{
                        bhits:{doc_count:-1},
                        hsps:{hsps:{doc_count:-1}}
                    }
                };
                console.log(ret);
            });
        }
    });
};

function main(err, content) {
    var bd = JSON.parse(content);
    var doc = {};
    doc._id = argv.infile;
    doc.BlastOutput2 = bd.BlastOutput2[0];
    MongoClient.connect(url, function (err, db) {
        assert.equal(null, err);
        console.log("Connected to the server: " + url);
        indexBlastOutfile(db, doc, function () {
            exports.querymongodb("test");
            db.close();
        });
    });
}

var indexBlastOutfile = function (db, blastdoc, callback) {
    var collection = db.collection('xml2');
    var id = blastdoc._id;

    var brr = collection.findOneAndDelete({ "_id": id });
    console.log(brr)
    if (1 === 2 && brr === undefined) {
        console.log("replace: " + id);
        collection.replaceOne({ "_id": id }, doc);
    }
    else {
        collection.insertOne(blastdoc,
            function (err, result) {
                assert.equal(err, null);
                console.log("BLAST document inserted");
                callback(result);
            });
    }
};


if (argv.infile !== undefined)
    fs.readFile(argv.infile, 'utf8', main);
