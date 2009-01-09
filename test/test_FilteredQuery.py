# ====================================================================
#   Copyright (c) 2004-2008 Open Source Applications Foundation
#
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
from lucene import *


class FilteredQueryTestCase(TestCase):
    """
    Unit tests ported from Java Lucene
    """

    def setUp(self):

        self.directory = RAMDirectory()
        writer = IndexWriter(self.directory, WhitespaceAnalyzer(), True)

        doc = Document()
        doc.add(Field("field", "one two three four five",
                      Field.Store.YES, Field.Index.TOKENIZED))
        doc.add(Field("sorter", "b",
                      Field.Store.YES, Field.Index.TOKENIZED))
                      
        writer.addDocument(doc)

        doc = Document()
        doc.add(Field("field", "one two three four",
                      Field.Store.YES, Field.Index.TOKENIZED))
        doc.add(Field("sorter", "d",
                      Field.Store.YES, Field.Index.TOKENIZED))

        writer.addDocument(doc)

        doc = Document()
        doc.add(Field("field", "one two three y",
                      Field.Store.YES, Field.Index.TOKENIZED))
        doc.add(Field("sorter", "a",
                      Field.Store.YES, Field.Index.TOKENIZED))

        writer.addDocument(doc)

        doc = Document()
        doc.add(Field("field", "one two x",
                      Field.Store.YES, Field.Index.TOKENIZED))
        doc.add(Field("sorter", "c",
                      Field.Store.YES, Field.Index.TOKENIZED))
                      
        writer.addDocument(doc)

        writer.optimize()
        writer.close()

        self.searcher = IndexSearcher(self.directory)
        self.query = TermQuery(Term("field", "three"))

        class filter(PythonFilter):
            def bits(self, reader):
                bitset = BitSet(5)
                bitset.set(1)
                bitset.set(3)
                return bitset

        self.filter = filter()

    def tearDown(self):

        self.searcher.close()
        self.directory.close()

    def testFilteredQuery(self):

        filteredquery = FilteredQuery(self.query, self.filter)
        hits = self.searcher.search(filteredquery);
        self.assertEqual(1, hits.length())
        self.assertEqual(1, hits.id(0))

        hits = self.searcher.search(filteredquery, Sort("sorter"))
        self.assertEqual(1, hits.length())
        self.assertEqual(1, hits.id(0))

        filteredquery = FilteredQuery(TermQuery(Term("field", "one")),
                                      self.filter)
        hits = self.searcher.search(filteredquery)
        self.assertEqual(2, hits.length())

        filteredquery = FilteredQuery(TermQuery(Term("field", "x")),
                                      self.filter)
        hits = self.searcher.search(filteredquery)
        self.assertEqual(1, hits.length())
        self.assertEqual(3, hits.id(0))

        filteredquery = FilteredQuery(TermQuery(Term("field", "y")),
                                      self.filter)
        hits = self.searcher.search(filteredquery)
        self.assertEqual(0, hits.length())

    def testRangeQuery(self):
        """
        This tests FilteredQuery's rewrite correctness
        """
        
        rq = RangeQuery(Term("sorter", "b"), Term("sorter", "d"), True)
        filteredquery = FilteredQuery(rq, self.filter)
        hits = self.searcher.search(filteredquery)
        self.assertEqual(2, hits.length())


if __name__ == "__main__":
    import sys, lucene
    lucene.initVM(lucene.CLASSPATH)
    if '-loop' in sys.argv:
        sys.argv.remove('-loop')
        while True:
            try:
                main()
            except:
                pass
    else:
         main()
