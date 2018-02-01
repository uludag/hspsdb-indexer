# Index/Query scripts

This is Python source folder of the hspsdb project, for indexing and querying
sequence similarity search results.

## Search results in tabular format

* [indexHSPs.py](indexHSPs.py): Index similarity search results
  in tabular format
  

* [queryHSPs.py](queryHSPs.py): Query indexed similarity search results,
  find most represented genes and present them using PivotTable.js

  See main [readme](../readme.md) for example command lines

## Search results in SAM/BAM format

* [indexbam.py](indexbam.py): Index SAM BAM files with MongoDB,
  _at early stages of development_

  BAM files reading was initially based on
  [pybam](https://github.com/JohnLonginotto/pybam) library,
  latest version reads both BAM and SAM files by calling
  [pysam](https://github.com/pysam-developers/pysam) library functions
