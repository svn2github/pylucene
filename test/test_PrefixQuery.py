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

from org.apache.lucene.document import Document, Field, StringField
from org.apache.lucene.index import Term
from org.apache.lucene.search import PrefixQuery


class PrefixQueryTestCase(PyLuceneTestCase):
    """
    Unit tests ported from Java Lucene
    """

    def testPrefixQuery(self):

        writer = self.getWriter()

        categories = ["/Computers", "/Computers/Mac", "/Computers/Windows"]
        for category in categories:
            doc = Document()
            doc.add(Field("category", category, StringField.TYPE_STORED))
            writer.addDocument(doc)

        writer.close()

        query = PrefixQuery(Term("category", "/Computers"))
        searcher = self.getSearcher()
        topDocs = searcher.search(query, 50)
        self.assertEqual(3, topDocs.totalHits,
                         "All documents in /Computers category and below")

        query = PrefixQuery(Term("category", "/Computers/Mac"))
        topDocs = searcher.search(query, 50)
        self.assertEqual(1, topDocs.totalHits, "One in /Computers/Mac")


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
