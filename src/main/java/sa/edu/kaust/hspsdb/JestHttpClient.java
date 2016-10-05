package sa.edu.kaust.hspsdb;

import io.searchbox.client.JestClient;
import io.searchbox.client.JestClientFactory;
import io.searchbox.client.JestResult;
import io.searchbox.client.config.HttpClientConfig;
import io.searchbox.core.Bulk;
import io.searchbox.core.BulkResult;
import io.searchbox.core.Delete;
import io.searchbox.core.DocumentResult;
import io.searchbox.core.Index;
import io.searchbox.indices.Refresh;
import java.io.IOException;
import java.util.Collection;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 *
 */
public class JestHttpClient implements IndexerClient
{
    static Logger log = LoggerFactory.getLogger(JestHttpClient.class);
    JestClient client;

    public JestHttpClient(String url)
    {
        JestClientFactory factory = new JestClientFactory();
        factory.setHttpClientConfig(new HttpClientConfig
                .Builder(url)
                .multiThreaded(true).readTimeout(80000)
                .build());
        client = factory.getObject();
    }

    @Override
    public void index(String index, String type, Object source,
            String id) throws IOException, IndexerException
    {
        Index index_ = new Index.Builder(source).
                index(index).type(type).id(id).build();
        DocumentResult r = client.execute(index_);
        if(r.isSucceeded()==false)
        {
            log.error(r.getErrorMessage());
            throw new IndexerException(r.getErrorMessage());
        }
    }


    @Override
    public long indexb(String index, String type, Collection<String> source,
            String idprefix, long i)
            throws IOException, IndexerException
    {
        Bulk.Builder b = new Bulk.Builder();
        b.defaultIndex(index).defaultType(type);
        for(Object obj: source)
            b.addAction(new Index.Builder(obj).id(idprefix + (++i)).build());
        Bulk index_ = b.build();

        BulkResult r = client.execute(index_);
        if(r.isSucceeded()==false)
        {
            log.error(r.getErrorMessage());
            throw new IndexerException(r.getErrorMessage());
        }
        return i;
    }


    @Override
    public void deleteall(String index) throws IndexerException
    {
            log.error("'delete-all' not yet implemented");
    }


    @Override
    public void delete(String index, String type, String id)
            throws IndexerException
    {
        try {
            client.execute(new Delete.Builder(id)
                    .index(index)
                    .type(type)
                    .build());
        } catch (IOException ex) {
            log.error(ex.getMessage());
            throw new IndexerException(ex);
        }
    }


    @Override
    public void close()
    {
        client.shutdownClient();
    }

    @Override
    public void commit(String index) throws IndexerException
    {
        Refresh refresh = new Refresh.Builder().build();
        try {
            JestResult result = client.execute(refresh);
            if(!result.isSucceeded())
                throw new IndexerException(result.getErrorMessage());
        } catch (IOException ex) {
            throw new IndexerException(ex.getMessage());
        }
    }

    @Override
    public void optimize(String index) throws IndexerException
    {
        throw new IndexerException("'optimize' not yet implemented");
    }

}
