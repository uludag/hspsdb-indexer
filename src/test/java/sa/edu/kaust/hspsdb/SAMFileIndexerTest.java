package sa.edu.kaust.hspsdb;

import java.io.FileReader;
import org.testng.annotations.DataProvider;
import org.testng.annotations.Test;

import java.io.IOException;
import java.io.Reader;
import java.util.Properties;
import javax.xml.bind.JAXBException;
import org.testng.Assert;
import org.testng.annotations.BeforeClass;


public class SAMFileIndexerTest {
    String server, index;
    SAMFileIndexer indexer;

    /**
     * Read Elasticsearch test server and name of the index
     */
    @BeforeClass
    final void readTestServerSettings() throws IOException {
        String config = "./src/test/resources/hspsdb-tests.properties";
        Properties p = new Properties();
        Reader reader = new FileReader(config);
        p.load(reader);
        server = p.getProperty("server");
        index= p.getProperty("index");
        indexer = new SAMFileIndexer(server);
    }

    @DataProvider(name = "htsjdkTestCases")
    public Object[][] htsjdkTestCases() {
        final Object[][] scenarios = new Object[][]{
            {"block_compressed.sam.gz"},
            {"uncompressed.sam"},
            {"unsorted.sam"},
            {"compressed.bam"}
        };
        return scenarios;
    }

    @Test(dataProvider = "htsjdkTestCases")
    public void htsjdkTest(final String inputFile)
            throws JAXBException, IOException, IndexerException {
        String DIR = "src/test/resources/htsjdk/samtools/";
        long n = indexer.index(DIR + inputFile, index);
        Assert.assertTrue(n > 0);
    }

    @DataProvider(name = "Magic-BLAST-TestCases")
    public Object[][] magicBLAST_TestCases() {
        final Object[][] scenarios = new Object[][]{
            {"SRR317068-pairedfastq-search.sam", 10928}
        };
        return scenarios;
    }

    @Test(dataProvider = "Magic-BLAST-TestCases")
    public void magicBLAST_Test(final String inputFile, long n_mappings)
            throws JAXBException, IOException, IndexerException {
        String DIR = "src/test/resources/mbsearch/";
        long n = indexer.index(DIR + inputFile, index);
        System.out.println(n);
        Assert.assertEquals(n, n_mappings);
    }
}
