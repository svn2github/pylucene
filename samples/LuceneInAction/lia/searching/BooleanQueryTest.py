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

from lucene import\
    Term, BooleanQuery, IndexSearcher, RangeQuery, TermQuery, BooleanClause


class BooleanQueryTest(LiaTestCase):

    def testAnd(self):

        searchingBooks = TermQuery(Term("subject", "search"))
        currentBooks = RangeQuery(Term("pubmonth", "200401"),
                                  Term("pubmonth", "200412"), True)

        currentSearchingBooks = BooleanQuery()
        currentSearchingBooks.add(searchingBooks, BooleanClause.Occur.MUST)
        currentSearchingBooks.add(currentBooks, BooleanClause.Occur.MUST)

        searcher = IndexSearcher(self.directory)
        hits = searcher.search(currentSearchingBooks)

        self.assertHitsIncludeTitle(hits, "Lucene in Action")

    def testOr(self):

        methodologyBooks = TermQuery(Term("category",
                                          "/technology/computers/programming/methodology"))
        easternPhilosophyBooks = TermQuery(Term("category",
                                                "/philosophy/eastern"))

        enlightenmentBooks = BooleanQuery()
        enlightenmentBooks.add(methodologyBooks, BooleanClause.Occur.SHOULD)
        enlightenmentBooks.add(easternPhilosophyBooks, BooleanClause.Occur.SHOULD)

        searcher = IndexSearcher(self.directory)
        hits = searcher.search(enlightenmentBooks)
        print "or =", enlightenmentBooks

        self.assertHitsIncludeTitle(hits, "Extreme Programming Explained")
        self.assertHitsIncludeTitle(hits, u"Tao Te Ching \u9053\u5FB7\u7D93")
