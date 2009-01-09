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
     WhitespaceAnalyzer, Document, Field, IndexWriter, Term, MultiSearcher, \
     QueryFilter, RAMDirectory, IndexSearcher, TermQuery


class SecurityFilterTest(TestCase):

    def setUp(self):

        self.directory = RAMDirectory()
        writer = IndexWriter(self.directory, WhitespaceAnalyzer(), True)

        # Elwood
        document = Document()
        document.add(Field("owner", "elwood",
                           Field.Store.YES, Field.Index.UN_TOKENIZED))
        document.add(Field("keywords", "elwoods sensitive info",
                           Field.Store.YES, Field.Index.TOKENIZED))
        writer.addDocument(document)

        # Jake
        document = Document()
        document.add(Field("owner", "jake",
                           Field.Store.YES, Field.Index.UN_TOKENIZED))
        document.add(Field("keywords", "jakes sensitive info",
                           Field.Store.YES, Field.Index.TOKENIZED))
        writer.addDocument(document)

        writer.close()

    def testSecurityFilter(self):

        query = TermQuery(Term("keywords", "info"))

        searcher = IndexSearcher(self.directory)
        hits = searcher.search(query)
        self.assertEqual(2, len(hits), "Both documents match")

        jakeFilter = QueryFilter(TermQuery(Term("owner", "jake")))

        hits = searcher.search(query, jakeFilter)
        self.assertEqual(1, len(hits))
        self.assertEqual("jakes sensitive info", hits[0].get("keywords"),
                         "elwood is safe")
