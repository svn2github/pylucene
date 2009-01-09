# ====================================================================
# Copyright (c) 2004-2007 Open Source Applications Foundation.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions: 
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software. 
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
# ====================================================================
#

from lucene import \
     IndexWriter, IndexReader, IndexSearcher, \
     WhitespaceAnalyzer, Document, Field, Term, TermQuery

from lia.indexing.BaseIndexingTestCase import BaseIndexingTestCase


class DocumentUpdateTest(BaseIndexingTestCase):

    def testUpdate(self):

        self.assertEqual(1, self.getHitCount("city", "Amsterdam"))

        reader = IndexReader.open(self.dir)
        reader.deleteDocuments(Term("city", "Amsterdam"))
        reader.close()

        writer = IndexWriter(self.dir, self.getAnalyzer(), False)
        doc = Document()
        doc.add(Field("id", "1", Field.Store.YES, Field.Index.UN_TOKENIZED))
        doc.add(Field("country", "Russia",
                      Field.Store.YES, Field.Index.NO))
        doc.add(Field("contents", "St. Petersburg has lots of bridges",
                      Field.Store.NO, Field.Index.TOKENIZED))
        doc.add(Field("city", "St. Petersburg",
                      Field.Store.YES, Field.Index.TOKENIZED))
        writer.addDocument(doc)
        writer.optimize()
        writer.close()

        self.assertEqual(0, self.getHitCount("city", "Amsterdam"))
        self.assertEqual(1, self.getHitCount("city", "Petersburg"))


    def getAnalyzer(self):

        return WhitespaceAnalyzer()


    def getHitCount(self, fieldName, searchString):

        searcher = IndexSearcher(self.dir)
        t = Term(fieldName, searchString)
        query = TermQuery(t)
        hits = searcher.search(query)
        hitCount = hits.length()
        searcher.close()

        return hitCount
