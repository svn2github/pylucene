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
