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
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.util import Version


class NotTestCase(PyLuceneTestCase):
    """
    Unit tests ported from Java Lucene
    """
  
    def testNot(self):

        writer = self.getWriter(analyzer=SimpleAnalyzer(Version.LUCENE_CURRENT))

        d1 = Document()
        d1.add(Field("field", "a b", TextField.TYPE_STORED))

        writer.addDocument(d1)
        writer.commit()
        writer.close()

        searcher = self.getSearcher()
        query = QueryParser(Version.LUCENE_CURRENT, "field",
                            SimpleAnalyzer(Version.LUCENE_CURRENT)).parse("a NOT b")

        topDocs = searcher.search(query, 50)
        self.assertEqual(0, topDocs.totalHits)


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
