# ====================================================================
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
# ====================================================================

from unittest import TestCase, main
from PyLuceneTestCase import PyLuceneTestCase

from java.util import BitSet
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.document import Document, TextField
from org.apache.lucene.index import Term
from org.apache.lucene.search import \
    FilteredQuery, Sort, SortField, TermRangeQuery, TermQuery
from org.apache.lucene.util import Bits, DocIdBitSet, Version
from org.apache.pylucene.search import PythonFilter


class FilteredQueryTestCase(PyLuceneTestCase):
    """
    Unit tests ported from Java Lucene
    """

    def setUp(self):
        super(FilteredQueryTestCase, self).setUp()

        writer = self.getWriter(analyzer=WhitespaceAnalyzer(Version.LUCENE_CURRENT))

        doc = Document()
        doc.add(self.newField("field", "one two three four five",
                              TextField.TYPE_STORED))
        doc.add(self.newField("sorter", "b",
                              TextField.TYPE_STORED))
                      
        writer.addDocument(doc)

        doc = Document()
        doc.add(self.newField("field", "one two three four",
                              TextField.TYPE_STORED))
        doc.add(self.newField("sorter", "d",
                              TextField.TYPE_STORED))

        writer.addDocument(doc)

        doc = Document()
        doc.add(self.newField("field", "one two three y",
                              TextField.TYPE_STORED))
        doc.add(self.newField("sorter", "a",
                              TextField.TYPE_STORED))

        writer.addDocument(doc)

        doc = Document()
        doc.add(self.newField("field", "one two x",
                              TextField.TYPE_STORED))
        doc.add(self.newField("sorter", "c",
                              TextField.TYPE_STORED))
                      
        writer.addDocument(doc)

        writer.commit()
        writer.close()

        self.searcher = self.getSearcher()
        self.query = TermQuery(Term("field", "three"))

        class filter(PythonFilter):
            def getDocIdSet(self, context, acceptDocs):
                if acceptDocs is None:
                    acceptDocs = Bits.MatchAllBits(5)
                bitset = BitSet(5)
                if acceptDocs.get(1):
                    bitset.set(1)
                if acceptDocs.get(3):
                    bitset.set(3)
                return DocIdBitSet(bitset)

        self.filter = filter()

    def testFilteredQuery(self):

        filteredquery = FilteredQuery(self.query, self.filter)
        topDocs = self.searcher.search(filteredquery, 50)
        self.assertEqual(1, topDocs.totalHits)
        self.assertEqual(1, topDocs.scoreDocs[0].doc)

        topDocs = self.searcher.search(filteredquery, None, 50,
                                       Sort(SortField("sorter",
                                                      SortField.Type.STRING)))
        self.assertEqual(1, topDocs.totalHits)
        self.assertEqual(1, topDocs.scoreDocs[0].doc)

        filteredquery = FilteredQuery(TermQuery(Term("field", "one")),
                                      self.filter)
        topDocs = self.searcher.search(filteredquery, 50)
        self.assertEqual(2, topDocs.totalHits)

        filteredquery = FilteredQuery(TermQuery(Term("field", "x")),
                                      self.filter)
        topDocs = self.searcher.search(filteredquery, 50)
        self.assertEqual(1, topDocs.totalHits)
        self.assertEqual(3, topDocs.scoreDocs[0].doc)

        filteredquery = FilteredQuery(TermQuery(Term("field", "y")),
                                      self.filter)
        topDocs = self.searcher.search(filteredquery, 50)
        self.assertEqual(0, topDocs.totalHits)

    def testRangeQuery(self):
        """
        This tests FilteredQuery's rewrite correctness
        """

        rq = TermRangeQuery.newStringRange("sorter", "b", "d", True, True)
        filteredquery = FilteredQuery(rq, self.filter)
        scoreDocs = self.searcher.search(filteredquery, None, 1000).scoreDocs
        self.assertEqual(2, len(scoreDocs))


if __name__ == "__main__":
    import sys, lucene
    lucene.initVM()
    if '-loop' in sys.argv:
        sys.argv.remove('-loop')
        while True:
            try:
                main()
            except:
                pass
    else:
         main()
