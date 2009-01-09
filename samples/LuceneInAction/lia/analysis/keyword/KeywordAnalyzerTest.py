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
