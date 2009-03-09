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
