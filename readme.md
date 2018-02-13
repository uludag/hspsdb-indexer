HSPs-db project is an effort to develop index and query tools for
sequence similarity search results.

Current project is able to index
 - NCBI-BLAST results in json format, with Elasticsearch
 - Search results in BLAST tabular format, with MongoDB

## History and project structure

Initial effort of the project was for BLAST xml/json formats.
Later we wanted to support SAM Sequence Alignment/Map format as well.
For this we first worked with Java [HTSJDK](https://github.com/samtools/htsjdk) library.
Later we found pybam and pysam libraries as alternatives for reading SAM/BAM
files and have started adding Python code to the project.
For this reason project is not a pure Java or Python project,
and have project files for both languages; _pom.xml_, _setup.py_.

During early stages of the project we also implemented Node.js client scripts
for EMBL-EBI and NCBI, BLAST services; [ebi-sss-client.js](scripts/ebi-sss-client.js),
[ncbi-sss-client.js](scripts/ncbi-sss-client.js). This is why we have
also _package.json_ project file in the project root folder.
Modules required by these two client scripts can be installed
by running `npm install` from project root folder

### Installation

Download hspsdb project source code:

```bash
git clone https://bitbucket.org/hspsdb/hspsdb-indexer.git ./hspsdb
```

## Indexing and querying tabular results

### Requirements

- Running [MongoDB](https://www.mongodb.com) server

- [nosqlbiosets](https://bitbucket.org/hspsdb/nosql-biosets) project,
  for connecting search results with UniProt entries

  Local UniProt MongoDB index with nosqlbiosets project, 
  requires 5GB MongoDB space
  
  Download project source code and install required Python libraries:

    ```bash
    git clone https://bitbucket.org/hspsdb/nosql-biosets.git ./nosqlbiosets
    cd nosqlbiosets
    pip install -r requirements.txt --user
    ```
  Follow instructions on nosqlbiosets project UniProt [page](
  https://github.com/uludag/nosql-biosets/tree/master/nosqlbiosets/uniprot)
  to index UniProt Swiss-Prot xml dataset

- Install libraries required by the hspsdb project

    ```bash
    # change current directory to hspsdb folder downloaded earlier 
    cd ../hspsdb
    pip install -r requirements.txt --user
    ```

### Indexing

* [indexHSPs.py](./hspsdb/indexHSPs.py): Index similarity search results saved
 in tabular format, e.g. generated by [LAMBDA](https://github.com/seqan/lambda),
 [BLASTX](http://blast.ncbi.nlm.nih.gov),
 or [DIAMOND](https://github.com/bbuchfink/diamond)

    ```bash
    ./hspsdb/indexHSPs.py index --help
    ```
    ```
    usage: indexHSPs.py index [-h] [--pair PAIR] [--db DB] [--database DATABASE]
                              [--delimiter DELIMITER] [-u USER]
                              [--password PASSWORD] [--host HOST] [--port PORT]
                              infile sampleid collection
    
        Index similarity search results of a sample
        
    
    positional arguments:
      infile                Similarity search results in tabular format
      sampleid              Id of the sample the query sequences were sequenced
                            from
      collection            MongoDB collection, for indexing/collecting HSPs of
                            the study
    
    optional arguments:
      -h, --help            show this help message and exit
      --pair PAIR           -1
      --db DB               'MongoDB'
      --database DATABASE   'biosets'
      --delimiter DELIMITER
                            '\t'
      -u USER, --user USER  -
      --password PASSWORD   -
      --host HOST           -
      --port PORT           -
    ```

  Example command lines to index LAMBDA search results of sequencing reads from
two samples

    ```bash 
    ./hspsdb/indexHSPs.py index ~/studyk/cutadapt-lambda2/sample1.R1.m8 sample1 studyk --pair=1
    ./hspsdb/indexHSPs.py index ~/studyk/cutadapt-lambda2/sample1.R2.m8 sample1 studyk --pair=2
    ./hspsdb/indexHSPs.py index ~/studyk/cutadapt-lambda2/sample2.R1.m8 sample2 studyk --pair=1
    ./hspsdb/indexHSPs.py index ~/studyk/cutadapt-lambda2/sample2.R2.m8 sample2 studyk --pair=2  
     ```

  Default values for MongoDB connection are read from nosql-biosets project
`conf/dbservers.json` configuration file 

## Querying

* [queryHSPs.py](./hspsdb/queryHSPs.py): Query indexed similarity search results,
  find most abundant genes and present them using [PivotTable.js](https://pivottable.js.org/)
  
   ```bash
    ./hspsdb/queryHSPs.py topgenes --help
   ```

   ```
    usage: queryHSPs.py topgenes [-h] [--bitscore BITSCORE] [--mismatch MISMATCH]
                                 [--limit LIMIT] [--rows ROWS]
                                 study outfile
    
        Abundance of HSPs grouped by organisms, genes, and GO annotations.
        Query results are saved in a json file and as PivotTable.js html files
        
    
    positional arguments:
      study                Name of the MongoDB collection for HSPs of a study
      outfile              Name for the pivot table html file to be generated
    
    optional arguments:
      -h, --help           show this help message and exit
      --bitscore BITSCORE  Minimum bitscore of HSPs (default: 100)
      --mismatch MISMATCH  Maximum mismatch in HSPs (default: 1)
      --limit LIMIT        Maximum number of the groups in the aggreagted results
                           (default: 4000)
      --rows ROWS          Default rows for the output pivot table (default: 'GO
                           term, Gene')
   ```
  Query "studyk" MongoDB collection for HSPs with bitscore value >= 30,
  and have only 1 or 2 mismatches or none
  ```bash
  ./hspsdb/queryHSPs.py topgenes  studyk --outfile studyk-topgenes\
       --bitscore 30 --mismatch 2
    
  # Open generated html with Chrome 
  chrome studyk-topgenes.html   
  ```

*  Example _topgenes_ pivot table [report](
https://uludag.github.io/hspsdb-indexer/docs/example-topgenes.html), for UniProt
search results of a small set of [fastq files](
https://github.com/slowkow/snakefiles/tree/master/data/fastq) 

## Indexing/querying results in BLAST json format

Following steps describe how to index BLAST result files in json format. 

* Install [Elasticsearch](https://www.elastic.co)

  If you are new to Elasticsearch
  the easiest way is to [download Elasticsearch](
  https://www.elastic.co/downloads/elasticsearch) with the TAR option (~30M).
  After extracting the tar file just `cd` to your Elasticsearch folder
  and run `./bin/elasticsearch` command.

* Choose an Elasticsearch index name for your BLAST results
  and use [init-index.sh](scripts/init-index.sh)
  script to initialize your index

* If you already have your BLAST outputs in json format use
  [index.sh](scripts/index.sh)
  or [index-folder.sh](scripts/files2index.sh) scripts
  to index your output files.
  If you do not have BLAST results in json format and if you first want to
  see how HSPs-db is working,
  then you can use the sample results we have in the testdb folder.
  Call [files2index.sh](scripts/files2index.sh) script with argument `./testdb`
  followed by the index name you choose earlier, and the URL of your Elasticsearch
  server.
  If you already have outputs in BLAST *archive* format you can use
  `blast_formatter` command to regenerate your outputs in json format.
  We want to implement support for outputs in xml format
  but this has not been done yet

* For new BLAST searches it is best to produce outputs first in BLAST archive format
  then use `blast_formatter` to generate the outputs you normally read
  and the json output for indexing

* After indexing your BLAST results you can install
  [HSPs-db web interface](https://github.com/uludag/hspsdb-webcode)
  for querying and visualizing indexed BLAST results. We have not been able to
  write a command-line or Python query API yet.
  
  Latest version of the web interface for BLAST results in json format
  can be seen on a [test server](http://hspsdb-test.herokuapp.com)
  which is connected to an Elasticsearch server with a small set of sample
  BLAST results

## Projects that inspire us

* [gffutils](https://github.com/daler/gffutils) project:
  "GFF and GTF files are loaded into SQLite3 databases,
  allowing much more complex manipulation of hierarchical features
  (e.g., genes, transcripts, and exons) than is possible with plain-text methods
  alone" 

* We can say we want to achieve what the [MultiQC](http://multiqc.info) project
  has already achieved; "A modular tool to aggregate results from bioinformatics
  analyses across many samples into a single report", _with more dynamic reports_

* We can also say HSPs-db project has some similarity to the
 [SeQC](https://github.com/JohnLonginotto/SeQC) project whic is maintained
 by the developer of the 'pybam' library
 
 * https://www.monetdb.org/bam

## Copyright

HSPs-db project has been developed
at King Abdullah University of Science and Technology,
[http://www.kaust.edu.sa](http://www.kaust.edu.sa)

HSPs-db project is licensed with MIT license.
If you would like to support the project
with selecting a different license please let us know by creating an issue
on github project page.
We will help you with contacting the relavant bodies of KAUST.
