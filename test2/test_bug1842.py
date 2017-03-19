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
from org.apache.lucene.document import Document, Field, FieldType, StringField
from org.apache.lucene.index import Term, IndexOptions
from org.apache.lucene.search import TermQuery
from org.apache.lucene.util import BytesRefIterator


class Test_Bug1842(PyLuceneTestCase):

    def setUp(self):
        super(Test_Bug1842, self).setUp()

        self.analyzer = StandardAnalyzer()

        w1 = self.getWriter(analyzer=self.analyzer)
        doc1 = Document()

        ftype = FieldType()
        ftype.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)
        ftype.setTokenized(True)
        ftype.setStoreTermVectors(True)
        ftype.freeze()

        doc1.add(Field("all", "blah blah blah Gesundheit", ftype))
        doc1.add(Field('id', '1', StringField.TYPE_NOT_STORED))

        w1.addDocument(doc1)
        w1.close()

    def test_bug1842(self):

        reader = self.getReader()
        searcher = self.getSearcher()
        q = TermQuery(Term("id", '1'))
        topDocs = searcher.search(q, 50)

        termvec = reader.getTermVector(topDocs.scoreDocs[0].doc, "all")
        terms = []
        freqs = []
        termsEnum = termvec.iterator()
        for term in BytesRefIterator.cast_(termsEnum):
            terms.append(term.utf8ToString())
            freqs.append(termsEnum.totalTermFreq())
        terms.sort()
        self.assert_(terms == ['blah', 'gesundheit'])
        self.assert_(freqs == [3, 1])

if __name__ == '__main__':
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    unittest.main()
