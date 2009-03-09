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
