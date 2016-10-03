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

public class SAMFileIndexer {
    static Logger LOG = LoggerFactory.getLogger(SAMFileIndexer.class);
    static IndexerClient client;
    final DefaultSAMRecordFactory factory;

    public SAMFileIndexer(String server) throws JAXBException, IndexerException {
        client = new JestHttpClient(server);
        factory = new DefaultSAMRecordFactory();
    }


    public int index(String inputFile, String index)
            throws JAXBException, IOException, IndexerException {
        String type = "sam";
        Collection<String> s = new ArrayList<>();
        int i = 0;
        int j = 0;
        final File input = new File(inputFile);
        String id = input.getName();
        SamReaderFactory rf = SamReaderFactory.makeDefault();
        rf.validationStringency(ValidationStringency.SILENT);
        final SamReader reader = rf.samRecordFactory(factory).open(input);

        for (final SAMRecord rec : reader) {
            ++i;
            s.add(toJson_jsonj(rec));
            if(++j == 100)
            {
                client.indexb(index, type, s, id, i);
                s.clear();
                j = 0;
            }
        }
        if(j > 0)
        {
            client.indexb(index, type, s, id, i);
            i += j;
        }
        client.commit(index);
        CloserUtil.close(reader);
        return i;
    }


    public static String toJson_jsonj(SAMRecord r) throws JAXBException {
        JsonObject o = object(
                field("alignmentStart", r.getAlignmentStart()),
                field("cigarString", r.getCigarString()),
                field("duplicateReadFlag", r.getDuplicateReadFlag()),
                field("firstOfPairFlag", r.getFirstOfPairFlag()),
                field("flags", r.getFlags()),
                field("inferredInsertSize", r.getInferredInsertSize()),
                field("mappingQuality", r.getMappingQuality()),
                field("mateAlignmentStart", r.getMateAlignmentStart()),
                field("mateNegativeStrandFlag", r.getMateNegativeStrandFlag()),
                field("mateReferenceIndex", r.getMateReferenceIndex()),
                field("mateReferenceName", r.getMateReferenceName()),
                field("mateUnmappedFlag", r.getMateUnmappedFlag()),
                field("notPrimaryAlignmentFlag", r.getNotPrimaryAlignmentFlag()),
                field("properPairFlag", r.getProperPairFlag()),
                field("readFailsVendorQualityCheckFlag",
                        r.getReadFailsVendorQualityCheckFlag()),
                field("readName", r.getReadName()),
                field("readString", r.getReadString()),
                field("readNegativeStrandFlag", r.getReadNegativeStrandFlag()),
                field("readPairedFlag", r.getReadPairedFlag()),
                field("readUnmappedFlag", r.getReadUnmappedFlag())
        );

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
