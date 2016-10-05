package sa.edu.kaust.hspsdb;

import htsjdk.samtools.DefaultSAMRecordFactory;
import htsjdk.samtools.SAMRecord;
import htsjdk.samtools.SamReader;
import htsjdk.samtools.SamReaderFactory;
import htsjdk.samtools.ValidationStringency;
import htsjdk.samtools.util.CloserUtil;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import javax.xml.bind.JAXBException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import static com.github.jsonj.tools.JsonBuilder.field;
import static com.github.jsonj.tools.JsonBuilder.object;
import com.github.jsonj.JsonObject;
import com.github.jsonj.tools.JsonSerializer;
import htsjdk.samtools.SAMRecordFactory;

public class SAMFileIndexer {
    static Logger LOG = LoggerFactory.getLogger(SAMFileIndexer.class);
    static IndexerClient client;
    static int BATCH_SIZE = 1000;
    final SAMRecordFactory factory;

    public SAMFileIndexer(String server) throws JAXBException, IndexerException {
        client = new JestHttpClient(server);
        factory = new DefaultSAMRecordFactory();
    }

    
    public long index(String inputFile, String index)
            throws JAXBException, IOException, IndexerException {
        long n = 0; int j = 0;
        String doctype = "sam";
        LOG.info("Indexing {} to index {}", inputFile, index);
        Collection<String> s = new ArrayList<>();
        final File input = new File(inputFile);
        String id = input.getName();
        SamReaderFactory rf = SamReaderFactory.makeDefault();
        rf.validationStringency(ValidationStringency.SILENT);
        final SamReader reader = rf.samRecordFactory(factory).open(input);

        for (final SAMRecord rec : reader) {
            s.add(toJson_jsonj(rec));
            if(++j == BATCH_SIZE) {
                n = client.indexb(index, doctype, s, id, n);
                s.clear();
                j = 0;
            }
        }
        if(j > 0) n = client.indexb(index, doctype, s, id, n);

        client.commit(index);
        CloserUtil.close(reader);
        LOG.info("{} mappings has been indexed", n);
        return n;
    }
    
    public static String toJson_jsonj(SAMRecord r) throws JAXBException {
        JsonObject o = object(
                field("alignmentStart", r.getAlignmentStart()),
                field("cigarString", r.getCigarString()),
                field("duplicateReadFlag", r.getDuplicateReadFlag()),
                field("flags", r.getFlags()),
                field("inferredInsertSize", r.getInferredInsertSize()),
                field("mappingQuality", r.getMappingQuality()),
                field("mateAlignmentStart", r.getMateAlignmentStart()),
                field("mateReferenceIndex", r.getMateReferenceIndex()),
                field("mateReferenceName", r.getMateReferenceName()),
                field("notPrimaryAlignmentFlag", r.getNotPrimaryAlignmentFlag()),
                field("readFailsVendorQualityCheckFlag",
                        r.getReadFailsVendorQualityCheckFlag()),
                field("readName", r.getReadName()),
                field("readString", r.getReadString()),
                field("readNegativeStrandFlag", r.getReadNegativeStrandFlag()),
                field("readPairedFlag", r.getReadPairedFlag()),
                field("readUnmappedFlag", r.getReadUnmappedFlag())
        );
        
        try{
            o.put("firstOfPairFlag", r.getFirstOfPairFlag());
            o.put("mateNegativeStrandFlag", r.getMateNegativeStrandFlag());
            o.put("mateUnmappedFlag", r.getMateUnmappedFlag());
            o.put("properPairFlag", r.getProperPairFlag());
        } catch (IllegalStateException e)
        {
            LOG.debug(e.getMessage());
        }
        
        String result = JsonSerializer.serialize(o);
        LOG.debug(result);
        return result;
    }
    

    public static void main(String[] a) throws IndexerException, JAXBException,
            IOException {
        String infile = a[0];
        String index = a[1];
        String server = a[2];
        SAMFileIndexer r = new SAMFileIndexer(server);
        r.index(infile, index);
    }
}
