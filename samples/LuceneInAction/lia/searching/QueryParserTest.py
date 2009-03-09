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
     WhitespaceAnalyzer, StandardAnalyzer, Term, QueryParser, Locale, \
     BooleanQuery, FuzzyQuery, IndexSearcher, RangeQuery, TermQuery, \
     BooleanClause


class QueryParserTest(LiaTestCase):

    def setUp(self):

        super(QueryParserTest, self).setUp()
        self.analyzer = WhitespaceAnalyzer()
        self.searcher = IndexSearcher(self.directory)

    def testToString(self):

        query = BooleanQuery()
        query.add(FuzzyQuery(Term("field", "kountry")),
                  BooleanClause.Occur.MUST)
        query.add(TermQuery(Term("title", "western")),
                  BooleanClause.Occur.SHOULD)

        self.assertEqual("+kountry~0.5 title:western",
                         query.toString("field"), "both kinds")

    def testPrefixQuery(self):

        parser = QueryParser("category", StandardAnalyzer())
        parser.setLowercaseExpandedTerms(False)

        print parser.parse("/Computers/technology*").toString("category")

    def testGrouping(self):

        query = QueryParser("subject", self.analyzer).parse("(agile OR extreme) AND methodology")
        hits = self.searcher.search(query)

        self.assertHitsIncludeTitle(hits, "Extreme Programming Explained")
        self.assertHitsIncludeTitle(hits, "The Pragmatic Programmer")

    def testRangeQuery(self):

        parser = QueryParser("subject", self.analyzer) 
        parser.setUseOldRangeQuery(True)

        query = parser.parse("pubmonth:[200401 TO 200412]")

        self.assert_(RangeQuery.instance_(query))

        hits = self.searcher.search(query)
        self.assertHitsIncludeTitle(hits, "Lucene in Action")

        query = QueryParser("pubmonth",
                            self.analyzer).parse("{200201 TO 200208}")

        hits = self.searcher.search(query)
        self.assertEqual(0, hits.length(), "JDwA in 200208")
  
    def testDateRangeQuery(self):

        # locale diff between jre and gcj 1/1/04 -> 01/01/04
        # expression = "modified:[1/1/04 TO 12/31/04]"
        
        expression = "modified:[01/01/04 TO 12/31/04]"
        parser = QueryParser("subject", self.analyzer)
        parser.setLocale(Locale.US)
        query = parser.parse(expression)
        print expression, "parsed to", query

        hits = self.searcher.search(query)
        self.assert_(hits.length() > 0)

    def testSlop(self):

        q = QueryParser("field", self.analyzer).parse('"exact phrase"')
        self.assertEqual("\"exact phrase\"", q.toString("field"),
                         "zero slop")

        qp = QueryParser("field", self.analyzer)
        qp.setPhraseSlop(5)
        q = qp.parse('"sloppy phrase"')
        self.assertEqual("\"sloppy phrase\"~5", q.toString("field"),
                         "sloppy, implicitly")

    def testPhraseQuery(self):

        q = QueryParser("field",
                        StandardAnalyzer()).parse('"This is Some Phrase*"')
        self.assertEqual("\"some phrase\"", q.toString("field"), "analyzed")

        q = QueryParser("field", self.analyzer).parse('"term"')
        self.assert_(TermQuery.instance_(q), "reduced to TermQuery")

    def testLowercasing(self):

        q = QueryParser("field", self.analyzer).parse("PrefixQuery*")
        self.assertEqual("prefixquery*", q.toString("field"), "lowercased")

        qp = QueryParser("field", self.analyzer)
        qp.setLowercaseExpandedTerms(False)
        q = qp.parse("PrefixQuery*")
        self.assertEqual("PrefixQuery*", q.toString("field"), "not lowercased")

    def testWildcard(self):

        try:
            QueryParser("field", self.analyzer).parse("*xyz")
            self.fail("Leading wildcard character should not be allowed")
        except:
            self.assert_(True)

    def testBoost(self):

         q = QueryParser("field", self.analyzer).parse("term^2")
         self.assertEqual("term^2.0", q.toString("field"))

    def testParseException(self):

        try:
            QueryParser("contents", self.analyzer).parse("^&#")
        except:
            # expression is invalid, as expected
            self.assert_(True)
        else:
            self.fail("ParseException expected, but not thrown")

#  public void testStopWord() throws ParseException {
#    Query q = QueryParser.parse("the AND drag", "field",
#        StopAnalyzer())
#    //  QueryParser fails on the previous line - this is a known 
#    //  issue
#  }
