import unittest
import scripts.alpha.indexbam as ibam


class BAMReaderTestCase(unittest.TestCase):
    def test_reader(self):
        infile = "../src/test/resources/htsjdk/samtools/compressed.bam"
        reader = ibam.BAMReader(infile)
        l = [r['readLength'] for r in reader.read_bam()]
        self.assertEqual(len(l), 10)

    def test_index(self):
        infile = "../src/test/resources/htsjdk/samtools/compressed.bam"
        r = ibam.index(infile, 'hspsdb-tests')
        self.assertEqual(r, 10)


if __name__ == '__main__':
    unittest.main()
