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

import sys, lucene, unittest
from PyLuceneTestCase import PyLuceneTestCase

from org.apache.lucene.analysis.core import SimpleAnalyzer
from org.apache.lucene.document import Document, Field, TextField
from org.apache.lucene.index import Term
from org.apache.lucene.sandbox.queries.regex import RegexQuery
from org.apache.lucene.search.spans import \
    SpanMultiTermQueryWrapper, SpanNearQuery


class TestRegexQuery(PyLuceneTestCase):
    FN = "field"

    def setUp(self):
        super(TestRegexQuery, self).setUp()

        writer = self.getWriter(analyzer=SimpleAnalyzer(self.TEST_VERSION))
        doc = Document()
        doc.add(Field(self.FN, "the quick brown fox jumps over the lazy dog", TextField.TYPE_NOT_STORED))
        writer.addDocument(doc)
        writer.commit()
        writer.close()
        self.searcher = self.getSearcher()

    def tearDown(self):

        del self.searcher
        super(TestRegexQuery, self).tearDown()

    def newTerm(self, value):
  
        return Term(self.FN, value)

    def regexQueryNrHits(self, regex):

        query = RegexQuery(self.newTerm(regex))

        return self.searcher.search(query, 50).totalHits

    def spanRegexQueryNrHits(self, regex1, regex2, slop, ordered):

        srq1 = SpanMultiTermQueryWrapper(RegexQuery(self.newTerm(regex1)))
        srq2 = SpanMultiTermQueryWrapper(RegexQuery(self.newTerm(regex2)))
        query = SpanNearQuery([srq1, srq2], slop, ordered)

        return self.searcher.search(query, 50).totalHits

    def testRegex1(self):

        self.assertEqual(1, self.regexQueryNrHits("^q.[aeiou]c.*$"))

    def testRegex2(self):

        self.assertEqual(0, self.regexQueryNrHits("^.[aeiou]c.*$"))

    def testRegex3(self):

        self.assertEqual(0, self.regexQueryNrHits("^q.[aeiou]c$"))

    def testSpanRegex1(self):

        self.assertEqual(1, self.spanRegexQueryNrHits("^q.[aeiou]c.*$",
                                                      "dog", 6, True))

    def testSpanRegex2(self):

        self.assertEqual(0, self.spanRegexQueryNrHits("^q.[aeiou]c.*$",
                                                      "dog", 5, True))


if __name__ == "__main__":
    lucene.initVM()
    if '-loop' in sys.argv:
        sys.argv.remove('-loop')
        while True:
            try:
                unittest.main()
            except:
                pass
    else:
        unittest.main()
