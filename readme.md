# HSPs-db

This repository includes scripts for indexing sequence
similarity search results, either in NCBI-BLAST xml/json formats, tabular format,
or in SAM/BAM formats.

## History and project structure

Initial effort of the project was for BLAST xml/json files.
Later we wanted to support for SAM Sequence Alignment/Map format,
using JAVA HTSJDK library.
Later we have found pybam and pysam libraries as alternatives for reading SAM/BAM
files and have started adding Python scripts to the project.
For this reason project is not a pure Java, Python or JavaScript project.
We have project files for all these 3 languages; _pom.xml_, _setup.py_,
_package.json_.

Initally only Elasticsearch indexes were supported, later
MongoDB support added. In most recent work (support for tabular results)
we focus on MongoDB indexes and queries.

## Installation

Download hspsdb project source code and install required libraries:

```bash
git clone https://bitbucket.org/hspsdb/nosql-biosets.git ./nosqlbiosets
cd nosqlbiosets
pip install -r requirements.txt --user
git clone https://bitbucket.org/hspsdb/hspsdb-indexer.git ./hspsdb
cd hspsdb
pip install -r requirements.txt --user
```

* Install [Elasticsearch](https://www.elastic.co)

  If you are new to Elasticsearch and  you are using Linux
  the easiest way is to [download Elasticsearch](
  https://www.elastic.co/downloads/elasticsearch) with the TAR option (~30M).
  After extracting the tar file just `cd` to your Elasticsearch folder
  and run `./bin/elasticsearch` command.

## Indexing results in BLAST xml, json formats

Following steps describe how to index BLAST result files in xml/json formats. 
We will add new sections when the index scripts for SAM/BAM files and tabular
result files reach to a level of maturity.

* Choose an Elasticsearch index name for your BLAST results
  and use [init-index.sh](scripts/init-index.sh)
  script to initialize your index

* If you already have your BLAST outputs in json format use
  [index.sh](scripts/index.sh)
  or [index-folder.sh](scripts/files2index.sh) scripts
  to index your output files.
  If you do not have any BLAST results in json format and if you first want to
  see how HSPs-db is working,
  then you can use the sample results we have in the testdb folder.
  Call [files2index.sh](scripts/files2index.sh) script with argument `./testdb`
  followed by the index name you choose earlier, and the URL of your Elasticsearch
  server.
  If you already have outputs in BLAST archive format you can use
  `blast_formatter` command to regenerate your outputs in json format.
  We want to implement scripts that maps existing XML outputs to json format
  but this has not been done yet

* After you indexed your BLAST results you can install
 [HSPs-db web interface](https://github.com/uludag/hspsdb-webcode)
  for querying and visualizing indexed BLAST results

* For new BLAST searches it is best to produce outputs first in BLAST archive format
  then use `blast_formatter` to generate the outputs you normally read
  and the json output for indexing

* This repository also includes Node.js client scripts for EMBL-EBI and NCBI,
  BLAST services; [ebi-sss-client.js](scripts/ebi-sss-client.js),
  [ncbi-sss-client.js](scripts/ncbi-sss-client.js).
  Modules required by the scripts can be installed
  by running `npm install` from project root folder

## Similar work

* https://github.com/daler/gffutils:
  "GFF and GTF files are loaded into SQLite3 databases,
  allowing much more complex manipulation of hierarchical features
  (e.g., genes, transcripts, and exons) than is possible with plain-text methods
  alone"
  
  _nosql-biosets project doesn't yet have a level of maturity comparable
   to the gffutils library_.

* We can say we want to achieve what the [MultiQC](http://multiqc.info) project
  has already achieved; "A modular tool to aggregate results from bioinformatics
  analyses across many samples into a single report", _with more dynamic reports_.

* We can also say HSPs-db project has some similarity to the
 [SeQC](https://github.com/JohnLonginotto/SeQC) project whic is maintained
 by the developer of the 'pybam' library which we use for indexing BAM files
 
 * https://www.monetdb.org/Documentation/Extensions/LifeScience/load 

## Notes

In a separate repository we develop web interfaces for the indexed results,
[hspsdb-webcode](https://github.com/uludag/hspsdb-webcode).
Latest version of the web interface for BLAST results in xml/json outputs
can be seen on a [test server](http://hspsdb-test.herokuapp.com)
which is connected to an Elasticsearch server with a small set of sample
BLAST results.

## Copyright

HSPs-db project has been developed
at King Abdullah University of Science and Technology, http://www.kaust.edu.sa

HSPs-db project is licensed with MIT license.
