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
     WhitespaceAnalyzer, IndexSearcher, RAMDirectory, \
     Document, Field, IndexWriter, TermQuery, SpanNearQuery

from lia.extsearch.queryparser.NumberUtils import NumberUtils
from lia.extsearch.queryparser.CustomQueryParser import \
    MultiFieldCustomQueryParser, CustomQueryParser


class AdvancedQueryParserTest(TestCase):

    def setUp(self):

        self.analyzer = WhitespaceAnalyzer()
        self.directory = RAMDirectory()

        writer = IndexWriter(self.directory, self.analyzer, True)

        for i in xrange(1, 501):
            doc = Document()
            doc.add(Field("id", NumberUtils.pad(i),
                          Field.Store.YES, Field.Index.UN_TOKENIZED))
            writer.addDocument(doc)

        writer.close()

    def testCustomQueryParser(self):

        parser = CustomQueryParser("field", self.analyzer)

        try:
            parser.parse("a?t")
            self.fail("Wildcard queries should not be allowed")
        except:
            # expected
            self.assert_(True)

        try:
            parser.parse("xunit~")
            self.fail("Fuzzy queries should not be allowed")
        except:
            # expected
            self.assert_(True)

    def testCustomMultiFieldQueryParser(self):

        parser = MultiFieldCustomQueryParser(["field"], self.analyzer)

        try:
            parser.parse("a?t")
            self.fail("Wildcard queries should not be allowed")
        except:
            # expected
            self.assert_(True)

        try:
            parser.parse("xunit~")
            self.fail("Fuzzy queries should not be allowed")
        except:
            # expected
            self.assert_(True)

    def testIdRangeQuery(self):

        parser = CustomQueryParser("field", self.analyzer)

        query = parser.parse("id:[37 TO 346]")
        self.assertEqual("id:[0000000037 TO 0000000346]",
                         query.toString("field"), "padded")

        searcher = IndexSearcher(self.directory)
        hits = searcher.search(query)
        self.assertEqual(310, hits.length())

        print parser.parse("special:[term TO *]")
        print parser.parse("special:[* TO term]")

    def testPhraseQuery(self):

        parser = CustomQueryParser("field", self.analyzer)

        query = parser.parse("singleTerm")
        self.assert_(TermQuery.instance_(query), "TermQuery")

        query = parser.parse("\"a phrase\"")
        self.assert_(SpanNearQuery.instance_(query), "SpanNearQuery")
