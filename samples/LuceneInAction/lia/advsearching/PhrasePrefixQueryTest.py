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

from unittest import TestCase
from lucene import \
     WhitespaceAnalyzer, Document, Field, IndexWriter, Term, BooleanQuery, \
     IndexSearcher, PhrasePrefixQuery, PhraseQuery, RAMDirectory, BooleanClause


class PhrasePrefixQueryTest(TestCase):

    def setUp(self):

        directory = RAMDirectory()
        writer = IndexWriter(directory, WhitespaceAnalyzer(), True)

        doc1 = Document()
        doc1.add(Field("field", "the quick brown fox jumped over the lazy dog",
                       Field.Store.YES, Field.Index.TOKENIZED))
        writer.addDocument(doc1)

        doc2 = Document()
        doc2.add(Field("field", "the fast fox hopped over the hound",
                       Field.Store.YES, Field.Index.TOKENIZED))
        writer.addDocument(doc2)
        writer.close()

        self.searcher = IndexSearcher(directory)

    def testBasic(self):
        
        query = PhrasePrefixQuery()
        query.add([Term("field", "quick"), Term("field", "fast")])
        query.add(Term("field", "fox"))
        print query

        hits = self.searcher.search(query)
        self.assertEqual(1, len(hits), "fast fox match")

        query.setSlop(1)
        hits = self.searcher.search(query)
        self.assertEqual(2, len(hits), "both match")

    def testAgainstOR(self):

        quickFox = PhraseQuery()
        quickFox.setSlop(1)
        quickFox.add(Term("field", "quick"))
        quickFox.add(Term("field", "fox"))

        fastFox = PhraseQuery()
        fastFox.add(Term("field", "fast"))
        fastFox.add(Term("field", "fox"))

        query = BooleanQuery()
        query.add(quickFox, BooleanClause.Occur.SHOULD)
        query.add(fastFox, BooleanClause.Occur.SHOULD)
        hits = self.searcher.search(query)
        self.assertEqual(2, len(hits))

    def debug(self, hits):

        for i, doc in hits:
            print "%s: %s" %(hits.score(i), doc['field'])
