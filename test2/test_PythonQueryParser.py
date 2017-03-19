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

from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import Term
from org.apache.lucene.search import BooleanClause, TermQuery
from org.apache.pylucene.queryparser.classic import \
    PythonQueryParser, PythonMultiFieldQueryParser


class BooleanTestMixin(object):

    def getBooleanQuery(self, clauses):

        extra_query = TermQuery(Term("all", "extra_clause"))
        extra_clause = BooleanClause(extra_query, BooleanClause.Occur.SHOULD)
        clauses.add(extra_clause)

        return super(BooleanTestMixin, self).getBooleanQuery(clauses)


class PythonQueryParserTestCase(PyLuceneTestCase):

    def testOverrideBooleanQuery(self):

        class TestQueryParser(BooleanTestMixin, PythonQueryParser):
            def getFieldQuery_quoted(_self, field, queryText, quoted):
                return super(TestQueryParser, _self).getFieldQuery_quoted_super(field, queryText, quoted)

        qp = TestQueryParser('all', StandardAnalyzer())

        q = qp.parse("foo bar")
        self.assertEquals(str(q), "all:foo all:bar all:extra_clause")


class PythonMultiFieldQueryParserTestCase(PyLuceneTestCase):

    def testOverrideBooleanQuery(self):

        class TestQueryParser(BooleanTestMixin, PythonMultiFieldQueryParser):
            def getFieldQuery_quoted(_self, field, queryText, quoted):
                return super(TestQueryParser, _self).getFieldQuery_quoted_super(field, queryText, quoted)

        qp = TestQueryParser(['one', 'two'], StandardAnalyzer())
        q = qp.parse("foo bar", ['one', 'two'],
                     [BooleanClause.Occur.SHOULD, BooleanClause.Occur.SHOULD],
                     StandardAnalyzer())
        self.assertEquals(str(q), "(one:foo one:bar) (two:foo two:bar)")


if __name__ == "__main__":
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    if '-loop' in sys.argv:
        sys.argv.remove('-loop')
        while True:
            try:
                unittest.main()
            except:
                pass
    else:
         unittest.main()
