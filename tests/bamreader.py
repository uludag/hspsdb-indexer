import unittest
import hspsdb.indexbam as ibam

ES_INDEX = "hspsdb-tests"

class BAMReaderTestCase(unittest.TestCase):
    def test_reader(self):
        infile = "../src/test/resources/htsjdk/samtools/compressed.bam"
        reader = ibam.BAMReader(infile)
        l = [r['readLength'] for r in reader.read_bam()]
        self.assertEqual(len(l), 10)

    def test_index(self):
        infile = "../src/test/resources/htsjdk/samtools/compressed.bam"
        r = ibam.index(infile, ES_INDEX)
        self.assertEqual(r, 10)


if __name__ == '__main__':
    unittest.main()
