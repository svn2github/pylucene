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
     Term, BooleanQuery, IndexSearcher, TermQuery, DateField, \
     CachingWrapperFilter, DateFilter, RangeQuery, QueryFilter, BooleanClause
     

class FilterTest(LiaTestCase):

    def setUp(self):

        super(FilterTest, self).setUp()

        self.allBooks = RangeQuery(Term("pubmonth", "190001"),
                                   Term("pubmonth", "200512"), True)
        self.searcher = IndexSearcher(self.directory)
        hits = self.searcher.search(self.allBooks)
        self.numAllBooks = len(hits)

    def testDateFilter(self):

        jan1 = self.parseDate("2004-01-01")
        jan31 = self.parseDate("2004-01-31")
        dec31 = self.parseDate("2004-12-31")

        filter = DateFilter("modified", jan1, dec31)

        hits = self.searcher.search(self.allBooks, filter)
        self.assertEqual(self.numAllBooks, len(hits), "all modified in 2004")

        filter = DateFilter("modified", jan1, jan31)
        hits = self.searcher.search(self.allBooks, filter)
        self.assertEqual(0, len(hits), "none modified in January")

    def testQueryFilter(self):

        categoryQuery = TermQuery(Term("category", "/philosophy/eastern"))
        categoryFilter = QueryFilter(categoryQuery)

        hits = self.searcher.search(self.allBooks, categoryFilter)
        self.assertEqual(1, len(hits), "only tao te ching")

    def testFilterAlternative(self):

        categoryQuery = TermQuery(Term("category", "/philosophy/eastern"))

        constrainedQuery = BooleanQuery()
        constrainedQuery.add(self.allBooks, BooleanClause.Occur.MUST)
        constrainedQuery.add(categoryQuery, BooleanClause.Occur.MUST)

        hits = self.searcher.search(constrainedQuery)
        self.assertEqual(1, len(hits), "only tao te ching")

    def testQueryFilterWithRangeQuery(self):

        jan1 = self.parseDate("2004-01-01")
        dec31 = self.parseDate("2004-12-31")

        start = Term("modified", DateField.dateToString(jan1))
        end = Term("modified", DateField.dateToString(dec31))

        rangeQuery = RangeQuery(start, end, True)

        filter = QueryFilter(rangeQuery)
        hits = self.searcher.search(self.allBooks, filter)
        self.assertEqual(self.numAllBooks, len(hits), "all of 'em")

    def testCachingWrapper(self):

        jan1 = self.parseDate("2004-01-01")
        dec31 = self.parseDate("2004-12-31")

        dateFilter = DateFilter("modified", jan1, dec31)
        cachingFilter = CachingWrapperFilter(dateFilter)

        hits = self.searcher.search(self.allBooks, cachingFilter)
        self.assertEqual(self.numAllBooks, len(hits), "all of 'em")
