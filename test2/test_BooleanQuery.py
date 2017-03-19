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

from org.apache.lucene.index import Term
from org.apache.lucene.search import BooleanClause, BooleanQuery, TermQuery


class TestBooleanQuery(PyLuceneTestCase):
    """
    Unit tests ported from Java Lucene
    """

    def testEquality(self):

        b1 = BooleanQuery.Builder()
        b1.add(TermQuery(Term("field", "value1")), BooleanClause.Occur.SHOULD)
        b1.add(TermQuery(Term("field", "value2")), BooleanClause.Occur.SHOULD)
        bq1 = b1.build()

        n1 = BooleanQuery.Builder()
        n1.add(TermQuery(Term("field", "nestedvalue1")), BooleanClause.Occur.SHOULD)
        n1.add(TermQuery(Term("field", "nestedvalue2")), BooleanClause.Occur.SHOULD)
        nested1 = n1.build()
        b1.add(nested1, BooleanClause.Occur.SHOULD)
        bq1 = b1.build()

        b2 = BooleanQuery.Builder()
        b2.add(TermQuery(Term("field", "value1")), BooleanClause.Occur.SHOULD)
        b2.add(TermQuery(Term("field", "value2")), BooleanClause.Occur.SHOULD)

        n2 = BooleanQuery.Builder()
        n2.add(TermQuery(Term("field", "nestedvalue1")), BooleanClause.Occur.SHOULD)
        n2.add(TermQuery(Term("field", "nestedvalue2")), BooleanClause.Occur.SHOULD)
        nested2 = n2.build()
        b2.add(nested2, BooleanClause.Occur.SHOULD)
        bq2 = b2.build()

        self.assert_(bq1.equals(bq2))


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
