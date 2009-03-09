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
from lucene import *


class PrefixQueryTestCase(TestCase):
    """
    Unit tests ported from Java Lucene
    """

    def _initializeIndex(self, values):

        writer = IndexWriter(self.dir, WhitespaceAnalyzer(), True)
        for value in values:
            self._insertDoc(writer, value)
        writer.close()

    def _insertDoc(self, writer, content):

        doc = Document()

        doc.add(Field("id", "id" + str(self.docCount),
                      Field.Store.YES, Field.Index.UN_TOKENIZED))
        doc.add(Field("content", content,
                      Field.Store.NO, Field.Index.TOKENIZED))

        writer.addDocument(doc)
        self.docCount += 1

    def _addDoc(self, content):

        writer = IndexWriter(self.dir, WhitespaceAnalyzer(), False)
        self._insertDoc(writer, content)
        writer.close()

    def setUp(self):

        self.docCount = 0
        self.dir = RAMDirectory()

    def testExclusive(self):

        query = RangeQuery(Term("content", "A"),
                           Term("content", "C"),
                           False)
        self._initializeIndex(["A", "B", "C", "D"])
        searcher = IndexSearcher(self.dir)
        hits = searcher.search(query)
        self.assertEqual(1, hits.length(),
                         "A,B,C,D, only B in range")
        searcher.close()

        self._initializeIndex(["A", "B", "D"])
        searcher = IndexSearcher(self.dir)
        hits = searcher.search(query)
        self.assertEqual(1, hits.length(),
                         "A,B,D, only B in range")
        searcher.close()

        self._addDoc("C")
        searcher = IndexSearcher(self.dir)
        hits = searcher.search(query)
        self.assertEqual(1, hits.length(),
                         "C added, still only B in range")
        searcher.close()

    def testInclusive(self):

        query = RangeQuery(Term("content", "A"),
                           Term("content", "C"),
                           True)

        self._initializeIndex(["A", "B", "C", "D"])
        searcher = IndexSearcher(self.dir)
        hits = searcher.search(query)
        self.assertEqual(3, hits.length(),
                         "A,B,C,D - A,B,C in range")
        searcher.close()

        self._initializeIndex(["A", "B", "D"])
        searcher = IndexSearcher(self.dir)
        hits = searcher.search(query)
        self.assertEqual(2, hits.length(),
                         "A,B,D - A and B in range")
        searcher.close()

        self._addDoc("C")
        searcher = IndexSearcher(self.dir)
        hits = searcher.search(query)
        self.assertEqual(3, hits.length(),
                         "C added - A, B, C in range")
        searcher.close()


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
