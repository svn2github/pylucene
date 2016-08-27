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
from org.apache.pylucene.queryparser.classic import PythonQueryParser


class PythonExceptionTestCase(PyLuceneTestCase):
    def testThroughLayerException(self):
        class TestException(Exception):
            pass

        class TestQueryParser(PythonQueryParser):
            def getFieldQuery_quoted(_self, field, queryText, quoted):
                raise TestException("TestException")

        qp = TestQueryParser('all', StandardAnalyzer())

        with self.assertRaises(TestException):
            qp.parse("foo bar")


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
