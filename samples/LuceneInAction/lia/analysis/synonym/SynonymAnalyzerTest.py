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
