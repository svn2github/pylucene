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
from lia.extsearch.filters.MockSpecialsAccessor import MockSpecialsAccessor
from lia.extsearch.filters.SpecialsFilter import SpecialsFilter

from lucene import \
     WildcardQuery, FilteredQuery, TermQuery, BooleanQuery, RangeQuery, \
     IndexSearcher, Term, BooleanClause


class SpecialsFilterTest(LiaTestCase):

    def setUp(self):

        super(SpecialsFilterTest, self).setUp()

        self.allBooks = RangeQuery(Term("pubmonth", "190001"),
                                   Term("pubmonth", "200512"), True)
        self.searcher = IndexSearcher(self.directory)

    def testCustomFilter(self):

        isbns = ["0060812451", "0465026567"]
        accessor = MockSpecialsAccessor(isbns)
        
        filter = SpecialsFilter(accessor)
        hits = self.searcher.search(self.allBooks, filter)
        self.assertEquals(len(isbns), len(hits), "the specials")

    def testFilteredQuery(self):
        
        isbns = ["0854402624"]  # Steiner

        accessor = MockSpecialsAccessor(isbns)
        filter = SpecialsFilter(accessor)

        educationBooks = WildcardQuery(Term("category", "*education*"))
        edBooksOnSpecial = FilteredQuery(educationBooks, filter)

        logoBooks = TermQuery(Term("subject", "logo"))

        logoOrEdBooks = BooleanQuery()
        logoOrEdBooks.add(logoBooks, BooleanClause.Occur.SHOULD)
        logoOrEdBooks.add(edBooksOnSpecial, BooleanClause.Occur.SHOULD)

        hits = self.searcher.search(logoOrEdBooks)
        print logoOrEdBooks
        self.assertEqual(2, len(hits), "Papert and Steiner")
