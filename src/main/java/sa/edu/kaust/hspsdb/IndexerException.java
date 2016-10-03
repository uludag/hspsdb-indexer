package sa.edu.kaust.hspsdb;

/**
 *
 */
public class IndexerException extends Exception
{

    /**
     * Creates a new instance of <code>IndexerException</code> without detail
     * message.
     */
    public IndexerException()
    {
    }

    public IndexerException(Exception e)
    {
        super(e);
    }

    /**
     * Constructs an instance of <code>IndexerException</code> with the
     * specified detail message.
     *
     * @param msg the detail message.
     */
    public IndexerException(String msg)
    {
        super(msg);
    }
}
