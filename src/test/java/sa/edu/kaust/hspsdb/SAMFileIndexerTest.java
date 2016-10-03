package sa.edu.kaust.hspsdb;

import java.io.FileReader;
import org.testng.annotations.DataProvider;
import org.testng.annotations.Test;

import java.io.IOException;
import java.io.Reader;
import java.util.Properties;
import javax.xml.bind.JAXBException;
import org.testng.Assert;

public class SAMFileIndexerTest {
    private static final String TEST_DATA_DIR
            = "src/test/resources/htsjdk/samtools/";

    @DataProvider(name = "htsjdkTestCases")
    public Object[][] variousFormatReaderTestCases() {
        final Object[][] scenarios = new Object[][]{
            {"block_compressed.sam.gz"},
            {"uncompressed.sam"},
            {"unsorted.sam"},
            {"compressed.bam"}
        };
        return scenarios;
    }


    @Test(dataProvider = "htsjdkTestCases")
    public void samRecordFactoryTest(final String inputFile)
            throws JAXBException, IOException, IndexerException {
        Properties p = getHspsdbTestServer();
        String server = p.getProperty("server");
        String index= p.getProperty("index");

        SAMFileIndexer r = new SAMFileIndexer(server);
        int i = r.index(TEST_DATA_DIR + inputFile, index);
        Assert.assertTrue(i > 0);
    }


    static private Properties getHspsdbTestServer()
            throws IOException{
        String config = "./src/test/resources/hspsdb-tests.properties";
        Properties p = new Properties();
        Reader reader = new FileReader(config);
        p.load(reader);
        return p;
    }
}
