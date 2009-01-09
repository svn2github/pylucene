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
     IndexWriter, Term, RAMDirectory, Document, Field, \
     IndexSearcher, QueryParser

from lia.analysis.AnalyzerUtils import AnalyzerUtils
from lia.analysis.positional.PositionalPorterStopAnalyzer import \
     PositionalPorterStopAnalyzer


class PositionalPorterStopAnalyzerTest(TestCase):

    porterAnalyzer = PositionalPorterStopAnalyzer()
    
    def setUp(self):

        self.directory = RAMDirectory()
        writer = IndexWriter(self.directory, self.porterAnalyzer, True)

        doc = Document()
        doc.add(Field("contents",
                      "The quick brown fox jumps over the lazy dogs",
                       Field.Store.YES, Field.Index.TOKENIZED))
        writer.addDocument(doc)
        writer.close()

    def testStems(self):
        
        searcher = IndexSearcher(self.directory)
        query = QueryParser("contents", self.porterAnalyzer).parse("laziness")
        hits = searcher.search(query)

        self.assertEqual(1, hits.length(), "lazi")

        query = QueryParser("contents",
                            self.porterAnalyzer).parse('"fox jumped"')
        hits = searcher.search(query)

        self.assertEqual(1, hits.length(), "jump jumps jumped jumping")

    def testExactPhrase(self):

        searcher = IndexSearcher(self.directory)
        query = QueryParser("contents",
                            self.porterAnalyzer).parse('"over the lazy"')
        hits = searcher.search(query)

        self.assertEqual(0, hits.length(), "exact match not found!")

    def testWithSlop(self):

        searcher = IndexSearcher(self.directory)

        parser = QueryParser("contents", self.porterAnalyzer)
        parser.setPhraseSlop(1)

        query = parser.parse('"over the lazy"')
        hits = searcher.search(query)

        self.assertEqual(1, hits.length(), "hole accounted for")

    def main(cls):

        text = "The quick brown fox jumps over the lazy dogs"
        AnalyzerUtils.displayTokensWithPositions(cls.porterAnalyzer, text)
        print ''
        
    main = classmethod(main)
