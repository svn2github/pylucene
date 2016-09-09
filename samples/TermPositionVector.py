
import lucene

from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.store import RAMDirectory
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.util import BytesRef, BytesRefIterator
from org.apache.lucene.index import \
    IndexWriterConfig, IndexWriter, DirectoryReader, IndexOptions

if __name__ == '__main__':
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])

directory = RAMDirectory()
iconfig = IndexWriterConfig(LimitTokenCountAnalyzer(StandardAnalyzer(), 100))
iwriter = IndexWriter(directory, iconfig)

ft = FieldType()
ft.setStored(True)
ft.setTokenized(True)
ft.setStoreTermVectors(True)
ft.setStoreTermVectorOffsets(True)
ft.setStoreTermVectorPositions(True)
ft.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS_AND_OFFSETS)

ts = ["this bernhard is the text to be index text",
      "this claudia is the text to be indexed"]
for t in ts:
    doc = Document()
    doc.add(Field("fieldname", t, ft))
    iwriter.addDocument(doc)

iwriter.commit()
iwriter.close()
ireader = DirectoryReader.open(directory)

for doc in xrange(0, len(ts)):
    tv = ireader.getTermVector(doc, "fieldname")
    termsEnum = tv.iterator()

    for term in BytesRefIterator.cast_(termsEnum):
        dpEnum = termsEnum.postings(None)
        dpEnum.nextDoc()  # prime the enum which works only for the current doc
        freq = dpEnum.freq()

        print 'term:', term.utf8ToString()
        print '  freq:', freq

        for i in xrange(freq):
            print "  pos:", dpEnum.nextPosition()
            print "  off: %i-%i" %(dpEnum.startOffset(), dpEnum.endOffset())
    print
