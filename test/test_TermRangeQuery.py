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

import sys, lucene, unittest
from PyLuceneTestCase import PyLuceneTestCase

from org.apache.lucene.document import Document, Field, StringField, TextField
from org.apache.lucene.index import IndexWriterConfig
from org.apache.lucene.search import TermRangeQuery


class TermRangeQueryTestCase(PyLuceneTestCase):
    """
    Unit tests ported from Java Lucene
    """

    def setUp(self):
        super(TermRangeQueryTestCase, self).setUp()

        self.docCount = 0

    def _initializeIndex(self, values):

        writer = self.getWriter()
        for value in values:
            self._insertDoc(writer, value)
        writer.close()

    def _insertDoc(self, writer, content):

        doc = Document()

        doc.add(Field("id", "id" + str(self.docCount),
                      StringField.TYPE_STORED))
        doc.add(Field("content", content,
                      TextField.TYPE_NOT_STORED))

        writer.addDocument(doc)
        self.docCount += 1

    def _addDoc(self, content):

        writer = self.getWriter(open_mode=IndexWriterConfig.OpenMode.APPEND)
        self._insertDoc(writer, content)
        writer.close()

    def testExclusive(self):

        query = TermRangeQuery.newStringRange("content", "A", "C", False, False)

        self._initializeIndex(["A", "B", "C", "D"])
        searcher = self.getSearcher()
        topDocs = searcher.search(query, 50)
        self.assertEqual(1, topDocs.totalHits,
                         "A,B,C,D, only B in range")
        del searcher

        self._initializeIndex(["A", "B", "D"])
        searcher = self.getSearcher()
        topDocs = searcher.search(query, 50)
        self.assertEqual(1, topDocs.totalHits,
                         "A,B,D, only B in range")
        del searcher

        self._addDoc("C")
        searcher = self.getSearcher()
        topDocs = searcher.search(query, 50)
        self.assertEqual(1, topDocs.totalHits,
                         "C added, still only B in range")
        del searcher

    def testInclusive(self):

        query = TermRangeQuery.newStringRange("content", "A", "C", True, True)

        self._initializeIndex(["A", "B", "C", "D"])
        searcher = self.getSearcher()
        topDocs = searcher.search(query, 50)
        self.assertEqual(3, topDocs.totalHits,
                         "A,B,C,D - A,B,C in range")
        del searcher

        self._initializeIndex(["A", "B", "D"])
        searcher = self.getSearcher()
        topDocs = searcher.search(query, 50)
        self.assertEqual(2, topDocs.totalHits,
                         "A,B,D - A and B in range")
        del searcher

        self._addDoc("C")
        searcher = self.getSearcher()
        topDocs = searcher.search(query, 50)
        self.assertEqual(3, topDocs.totalHits,
                         "C added - A, B, C in range")
        del searcher


if __name__ == "__main__":
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    if '-loop' in sys.argv:
        sys.argv.remove('-loop')
        while True:
            try:
                unittest.main()
            except:
                pass
    else:
         unittest.main()
