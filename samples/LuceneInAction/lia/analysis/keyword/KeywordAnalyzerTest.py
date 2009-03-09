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
     IndexWriter, Term, SimpleAnalyzer, PerFieldAnalyzerWrapper, \
     RAMDirectory, Document, Field, IndexSearcher, TermQuery, \
     QueryParser, Analyzer, StringReader, Token, JavaError

from lia.analysis.keyword.KeywordAnalyzer import KeywordAnalyzer
from lia.analysis.keyword.SimpleKeywordAnalyzer import SimpleKeywordAnalyzer


class KeywordAnalyzerTest(TestCase):

    def setUp(self):

        self.directory = RAMDirectory()
        writer = IndexWriter(self.directory, SimpleAnalyzer(), True)

        doc = Document()
        doc.add(Field("partnum", "Q36",
                      Field.Store.YES, Field.Index.UN_TOKENIZED))
        doc.add(Field("description", "Illidium Space Modulator",
                      Field.Store.YES, Field.Index.TOKENIZED))
        writer.addDocument(doc)
        writer.close()

        self.searcher = IndexSearcher(self.directory)

    def testTermQuery(self):

        query = TermQuery(Term("partnum", "Q36"))
        hits = self.searcher.search(query)
        self.assertEqual(1, hits.length())

    def testBasicQueryParser(self):
        
        query = QueryParser("description",
                            SimpleAnalyzer()).parse("partnum:Q36 AND SPACE")

        hits = self.searcher.search(query)
        self.assertEqual("+partnum:q +space", query.toString("description"),
                         "note Q36 -> q")
        self.assertEqual(0, hits.length(), "doc not found :(")

    def testPerFieldAnalyzer(self):

        analyzer = PerFieldAnalyzerWrapper(SimpleAnalyzer())
        analyzer.addAnalyzer("partnum", KeywordAnalyzer())

        query = QueryParser("description",
                            analyzer).parse("partnum:Q36 AND SPACE")
        hits = self.searcher.search(query)

        self.assertEqual("+partnum:Q36 +space", query.toString("description"),
                         "Q36 kept as-is")
        self.assertEqual(1, hits.length(), "doc found!")

    def testSimpleKeywordAnalyzer(self):

        analyzer = SimpleKeywordAnalyzer()

        input = "Hello World"
        ts = analyzer.tokenStream("dummy", StringReader(input))
        self.assertEqual(ts.next().termText(), input)
        self.assert_(not list(ts) is None)
        ts.close()
