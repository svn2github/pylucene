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
     StandardAnalyzer, RAMDirectory, IndexWriter, Term, Document, Field, \
     IndexSearcher, TermQuery, PhraseQuery, QueryParser

from lia.analysis.AnalyzerUtils import AnalyzerUtils
from lia.analysis.synonym.SynonymAnalyzer import SynonymAnalyzer
from lia.analysis.synonym.MockSynonymEngine import MockSynonymEngine


class SynonymAnalyzerTest(TestCase):

    synonymAnalyzer = SynonymAnalyzer(MockSynonymEngine())

    def setUp(self):

        self.directory = RAMDirectory()
        writer = IndexWriter(self.directory, self.synonymAnalyzer, True)

        doc = Document()
        doc.add(Field("content",
                      "The quick brown fox jumps over the lazy dogs",
                      Field.Store.YES, Field.Index.TOKENIZED))
        writer.addDocument(doc)
        writer.close()

        self.searcher = IndexSearcher(self.directory)

    def tearDown(self):

        self.searcher.close()

    def testJumps(self):

        tokens = AnalyzerUtils.tokensFromAnalysis(self.synonymAnalyzer, "jumps")
        AnalyzerUtils.assertTokensEqual(self, tokens,
                                        ["jumps", "hops", "leaps"])

        # ensure synonyms are in the same position as the original
        self.assertEqual(1, tokens[0].getPositionIncrement(), "jumps")
        self.assertEqual(0, tokens[1].getPositionIncrement(), "hops")
        self.assertEqual(0, tokens[2].getPositionIncrement(), "leaps")

    def testSearchByAPI(self):

        tq = TermQuery(Term("content", "hops"))
        hits = self.searcher.search(tq)
        self.assertEqual(1, len(hits))

        pq = PhraseQuery()
        pq.add(Term("content", "fox"))
        pq.add(Term("content", "hops"))
        hits = self.searcher.search(pq)
        self.assertEquals(1, len(hits))

    def testWithQueryParser(self):

        query = QueryParser("content",
                            self.synonymAnalyzer).parse('"fox jumps"')
        hits = self.searcher.search(query)
        # in Lucene 1.9, position increments are no longer ignored
        self.assertEqual(1, len(hits), "!!!! what?!")

        query = QueryParser("content", StandardAnalyzer()).parse('"fox jumps"')
        hits = self.searcher.search(query)
        self.assertEqual(1, len(hits), "*whew*")

    def main(cls):

        query = QueryParser("content", cls.synonymAnalyzer).parse('"fox jumps"')
        print "\"fox jumps\" parses to ", query.toString("content")

        print "From AnalyzerUtils.tokensFromAnalysis: "
        AnalyzerUtils.displayTokens(cls.synonymAnalyzer, "\"fox jumps\"")
        print ''
        
    main = classmethod(main)
