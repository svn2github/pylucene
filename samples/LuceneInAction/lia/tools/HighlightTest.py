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
     SimpleAnalyzer, Term, IndexSearcher, TermQuery, \
     Highlighter, QueryScorer, StringReader, Hit


class HighlightTest(LiaTestCase):

    def testHighlighting(self):

        text = "The quick brown fox jumps over the lazy dog"

        query = TermQuery(Term("field", "fox"))
        scorer = QueryScorer(query)
        highlighter = Highlighter(scorer)

        tokenStream = SimpleAnalyzer().tokenStream("field", StringReader(text))

        self.assertEqual("The quick brown <B>fox</B> jumps over the lazy dog",
                         highlighter.getBestFragment(tokenStream, text))

    def testHits(self):

        searcher = IndexSearcher(self.directory)
        query = TermQuery(Term("title", "action"))
        hits = searcher.search(query)

        scorer = QueryScorer(query)
        highlighter = Highlighter(scorer)

        for hit in hits:
            doc = Hit.cast_(hit).getDocument()
            title = doc["title"]
            stream = SimpleAnalyzer().tokenStream("title", StringReader(title))
            fragment = highlighter.getBestFragment(stream, title)
    
            print fragment
