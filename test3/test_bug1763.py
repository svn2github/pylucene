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
from org.apache.lucene.document import Document, Field, StoredField, TextField
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import RAMDirectory


class Test_Bug1763(PyLuceneTestCase):

    def setUp(self):
        super(Test_Bug1763, self).setUp()

        self.analyzer = StandardAnalyzer()
        self.d1 = RAMDirectory()
        self.d2 = RAMDirectory()

        w1, w2 = [self.getWriter(directory=d, analyzer=self.analyzer)
                  for d in [self.d1, self.d2]]
        doc1 = Document()
        doc2 = Document()
        doc1.add(Field("all", "blah blah double blah Gesundheit",
                       TextField.TYPE_NOT_STORED))
        doc1.add(Field('id', '1', StoredField.TYPE))
        doc2.add(Field("all", "a quick brown test ran over the lazy data",
                       TextField.TYPE_NOT_STORED))
        doc2.add(Field('id', '2', StoredField.TYPE))
        w1.addDocument(doc1)
        w2.addDocument(doc2)
        for w in [w1, w2]:
            w.close()

    def test_bug1763(self):

        w1 = self.getWriter(directory=self.d1, analyzer=self.analyzer)
        w1.addIndexes([self.d2])
        w1.close()

        searcher = self.getSearcher(self.d1)
        q = QueryParser('all', self.analyzer).parse('brown')
        topDocs = searcher.search(q, 50)
        self.assertEqual(searcher.doc(topDocs.scoreDocs[0].doc).get('id'), '2')


if __name__ == '__main__':
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    unittest.main()
