# ====================================================================
#   Copyright (c) 2004-2008 Open Source Applications Foundation
#
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

import unittest
from lucene import *

class Test_Bug1564(unittest.TestCase):

    def setUp(self):

        self.analyzer = StandardAnalyzer()
        self.store = RAMDirectory()

        writer = IndexWriter(self.store, self.analyzer, True)
        doc = Document()
        doc.add(Field('all', u'windowpane beplaster rapacious \
        catatonia gauntlet wynn depressible swede pick dressmake supreme \
        jeremy plumb theoretic bureaucracy causation chartres equipoise \
        dispersible careen heard',
                      Field.Store.NO, Field.Index.TOKENIZED))
        doc.add(Field('id', '1', Field.Store.YES, Field.Index.NO))
        writer.addDocument(doc)
        writer.optimize()
        writer.close()

    def tearDown(self):
        pass

    def test_bug1564(self):

        searcher = IndexSearcher(self.store)
        query = QueryParser('all', self.analyzer).parse('supreme')
        hits = searcher.search(query)
        self.assertEqual(hits.length(), 1)


if __name__ == '__main__':
    import lucene
    lucene.initVM(lucene.CLASSPATH)
    unittest.main()
