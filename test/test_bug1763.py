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

class Test_Bug1763(unittest.TestCase):

    def setUp(self):

        self.analyzer = StandardAnalyzer()
        self.d1 = RAMDirectory()
        self.d2 = RAMDirectory()
        
        w1, w2 = [IndexWriter(d, self.analyzer, True)
                  for d in [self.d1, self.d2]]
        doc1 = Document()
        doc2 = Document()
        doc1.add(Field("all", "blah blah double blah Gesundheit",
                       Field.Store.NO, Field.Index.TOKENIZED))
        doc1.add(Field('id', '1', Field.Store.YES, Field.Index.NO))
        doc2.add(Field("all", "a quick brown test ran over the lazy data",
                       Field.Store.NO, Field.Index.TOKENIZED))
        doc2.add(Field('id', '2',
                       Field.Store.YES, Field.Index.NO))
        w1.addDocument(doc1)
        w2.addDocument(doc2)
        for w in [w1, w2]:
            w.optimize()
            w.close()

    def tearDown(self):
        pass

    def test_bug1763(self):
            
        w1 = IndexWriter(self.d1, self.analyzer, True)
        w1.addIndexes([self.d2])
        w1.optimize()
        w1.close()

        searcher = IndexSearcher(self.d1)
        q = QueryParser('all', self.analyzer).parse('brown')
        hits = searcher.search(q)
        self.assertEqual(hits.doc(0).get('id'), '2')


if __name__ == '__main__':
    import lucene
    lucene.initVM(lucene.CLASSPATH)
    unittest.main()
