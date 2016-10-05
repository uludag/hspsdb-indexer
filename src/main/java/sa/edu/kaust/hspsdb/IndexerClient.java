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

    public void delete(String index, String type, String id)
            throws IndexerException;
    
    public void deleteall(String collection) throws IndexerException;
    
    public void index(String index, String type, Object source, String id)
            throws IOException, IndexerException;
    
    /**
     * Index given collection of docs using Elasticsearch batch API
     * @param index name of the Elasticsearch index
     * @param doctype type name for the documents
     * @param docs documents to index
     * @param idprefix prefix for document identifiers
     * @param i number to append to document identifiers
     * @return updated number with number of documents indexed
     * @throws IOException
     * @throws IndexerException 
     */
    public long indexb(String index, String doctype, Collection<String> docs,
            String idprefix, long i) throws IOException, IndexerException;

}
