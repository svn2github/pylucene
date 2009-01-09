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

from lia.common.LiaTestCase import LiaTestCase

from lucene import \
     WhitespaceAnalyzer, Document, Field, IndexWriter, Term, Explanation, \
     FuzzyQuery, IndexSearcher, Similarity, TermQuery, WildcardQuery, \
     RAMDirectory, PythonSimilarity


class ScoreTest(LiaTestCase):

    def setUp(self):

        super(ScoreTest, self).setUp()
        self.directory = RAMDirectory()

    def testSimple(self):

        class SimpleSimilarity(PythonSimilarity):

            def lengthNorm(self, field, numTerms):
                return 1.0

            def queryNorm(self, sumOfSquaredWeights):
                return 1.0

            def tf(self, freq):
                return freq

            def sloppyFreq(self, distance):
                return 2.0

            def idfTerms(self, terms, searcher):
                return 1.0

            def idfTerm(self, docFreq, numDocs):
                return 1.0

            def coord(self, overlap, maxOverlap):
                return 1.0

        self.indexSingleFieldDocs([Field("contents", "x", Field.Store.YES,
                                         Field.Index.TOKENIZED)])
        searcher = IndexSearcher(self.directory)
        searcher.setSimilarity(SimpleSimilarity())

        query = TermQuery(Term("contents", "x"))
        explanation = searcher.explain(query, 0)
        print explanation

        hits = searcher.search(query)
        self.assertEqual(1, hits.length())

        self.assertEqual(hits.score(0), 1.0)
        searcher.close()

    def indexSingleFieldDocs(self, fields):

        writer = IndexWriter(self.directory, WhitespaceAnalyzer(), True)

        for field in fields:
            doc = Document()
            doc.add(field)
            writer.addDocument(doc)

        writer.optimize()
        writer.close()

    def testWildcard(self):

        self.indexSingleFieldDocs([Field("contents", "wild", Field.Store.YES,
                                         Field.Index.TOKENIZED),
                                   Field("contents", "child", Field.Store.YES,
                                         Field.Index.TOKENIZED),
                                   Field("contents", "mild", Field.Store.YES,
                                         Field.Index.TOKENIZED),
                                   Field("contents", "mildew", Field.Store.YES,
                                         Field.Index.TOKENIZED)])

        searcher = IndexSearcher(self.directory)
        query = WildcardQuery(Term("contents", "?ild*"))
        hits = searcher.search(query)
        self.assertEqual(3, hits.length(), "child no match")

        self.assertEqual(hits.score(0), hits.score(1), "score the same")
        self.assertEqual(hits.score(1), hits.score(2), "score the same")

    def testFuzzy(self):

        self.indexSingleFieldDocs([Field("contents", "fuzzy", Field.Store.YES,
                                         Field.Index.TOKENIZED),
                                   Field("contents", "wuzzy", Field.Store.YES,
                                         Field.Index.TOKENIZED)])

        searcher = IndexSearcher(self.directory)
        query = FuzzyQuery(Term("contents", "wuzza"))
        hits = searcher.search(query)
        self.assertEqual(2, hits.length(), "both close enough")

        self.assert_(hits.score(0) !=  hits.score(1), "wuzzy closer than fuzzy")
        self.assertEqual("wuzzy", hits.doc(0).get("contents"), "wuzza bear")
