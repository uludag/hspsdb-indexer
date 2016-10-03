package sa.edu.kaust.hspsdb;

import java.io.IOException;
import java.util.Collection;

/**
 * Interface for Elasticsearch and Mongodb indexers
 */
public interface IndexerClient
{
    
    
    public void close() throws IndexerException;
    
    public void commit(String index) throws IndexerException;
            
    public void optimize(String index) throws IndexerException;

    public void deleteall(String collection) throws IndexerException;
    
    public void index(String index, String type, Object source, String id)
            throws IOException, IndexerException;
    
    public int indexb(String index, String type, Collection<String> source,
            String idprefix, int i) throws IOException, IndexerException;

}
