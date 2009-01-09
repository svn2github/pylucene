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
     WhitespaceAnalyzer, Document, Field, IndexWriter, Term, \
     IndexSearcher, PhraseQuery, RAMDirectory


class PhraseQueryTest(TestCase):

    def setUp(self):

        # set up sample document
        directory = RAMDirectory()
        writer = IndexWriter(directory, WhitespaceAnalyzer(), True)
        doc = Document()
        doc.add(Field("field", "the quick brown fox jumped over the lazy dog",
                       Field.Store.YES, Field.Index.TOKENIZED))
        writer.addDocument(doc)
        writer.close()

        self.searcher = IndexSearcher(directory)

    def matched(self, phrase, slop):

        query = PhraseQuery()
        query.setSlop(slop)

        for word in phrase:
            query.add(Term("field", word))

        hits = self.searcher.search(query)

        return len(hits) > 0

    def testSlopComparison(self):

        phrase = ["quick", "fox"]

        self.assert_(not self.matched(phrase, 0), "exact phrase not found")
        self.assert_(self.matched(phrase, 1), "close enough")

    def testReverse(self):

        phrase = ["fox", "quick"]

        self.assert_(not self.matched(phrase, 2), "hop flop")
        self.assert_(self.matched(phrase, 3), "hop hop slop")

    def testMultiple(self):

        self.assert_(not self.matched(["quick", "jumped", "lazy"], 3),
                     "not close enough")

        self.assert_(self.matched(["quick", "jumped", "lazy"], 4),
                     "just enough")

        self.assert_(not self.matched(["lazy", "jumped", "quick"], 7),
                     "almost but not quite")

        self.assert_(self.matched(["lazy", "jumped", "quick"], 8),
                     "bingo")
