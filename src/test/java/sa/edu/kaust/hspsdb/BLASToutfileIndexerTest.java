package sa.edu.kaust.hspsdb;

import com.google.common.io.LineReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;
import java.util.Properties;
import org.testng.annotations.AfterClass;
import org.testng.annotations.Test;

public class BLASToutfileIndexerTest
{
    String server;
    String index;
    String type = "xml2";
    static JestHttpClient client;

    final void readTestServerSettings() throws IOException {
        String config = "./src/test/resources/hspsdb-tests.properties";
        Properties p = new Properties();
        Reader reader = new FileReader(config);
        p.load(reader);
        server = p.getProperty("server");
        index= p.getProperty("xml2filesindex");
    }

    public BLASToutfileIndexerTest() throws IOException, IndexerException {
        readTestServerSettings();
        client = new JestHttpClient(server);
    }

    @AfterClass
    public static void close(){
        client.close();
    }

    String readBlastJsonOutfile(String infile) throws IOException
    {
        StringBuilder b = new StringBuilder(106200);
        Readable r = new FileReader(infile);
        LineReader lr = new LineReader(r);

        while(true){
            String ln = lr.readLine();
            if(ln == null) break;
            b.append(ln);
        }

        return b.toString();
    }

    @Test
    public void testWithBlastJson() throws IOException, IndexerException
    {
        String json;
        String[] ids= {"env_nr_search1", "env_nr_search2"};
        for(String id:ids)
        {
            json = readBlastJsonOutfile("./testdb/"+id+".json");
            client.index(index, type, json, id);
        }
    }
}
