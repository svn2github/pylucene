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
