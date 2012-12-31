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
from org.apache.lucene.search import \
    BooleanClause, BooleanQuery, Explanation, PhraseQuery, TermQuery
from org.apache.lucene.util import Version
from org.apache.pylucene.search import PythonCollector
from org.apache.pylucene.search.similarities import PythonDefaultSimilarity


class SimpleSimilarity(PythonDefaultSimilarity):

    def queryNorm(self, sumOfSquaredWeights):
        return 1.0

    def coord(self, overlap, maxOverlap):
        return 1.0

    def lengthNorm(self, state):
        return state.getBoost()

    def tf(self, freq):
        return freq

    def sloppyFreq(self, distance):
        return 2.0

    def idf(self, docFreq, numDocs):
        return 1.0

    def idfExplain(self, collectionStats, termStats):
        return Explanation(1.0, "inexplicable")


class SimilarityTestCase(PyLuceneTestCase):
    """
    Unit tests ported from Java Lucene
    """

    def testSimilarity(self):

        writer = self.getWriter(analyzer=SimpleAnalyzer(Version.LUCENE_CURRENT),
                                similarity=SimpleSimilarity())
    
        d1 = Document()
        d1.add(Field("field", "a c", TextField.TYPE_STORED))

        d2 = Document()
        d2.add(Field("field", "a b c", TextField.TYPE_STORED))
    
        writer.addDocument(d1)
        writer.addDocument(d2)
        writer.commit()
        writer.close()

        searcher = self.getSearcher()
        searcher.setSimilarity(SimpleSimilarity())

        a = Term("field", "a")
        b = Term("field", "b")
        c = Term("field", "c")

        class collector1(PythonCollector):
            def collect(_self, doc, score):
                self.assertEqual(1.0, score)
            def setNextReader(_self, context):
                pass
            def acceptsDocsOutOfOrder(_self):
                return True

        searcher.search(TermQuery(b), collector1())

        bq = BooleanQuery()
        bq.add(TermQuery(a), BooleanClause.Occur.SHOULD)
        bq.add(TermQuery(b), BooleanClause.Occur.SHOULD)

        class collector2(PythonCollector):
            def collect(_self, doc, score):
                self.assertEqual(doc + _self.base + 1, score)
            def setNextReader(_self, context):
                _self.base = context.docBase
            def acceptsDocsOutOfOrder(_self):
                return True

        searcher.search(bq, collector2())

        pq = PhraseQuery()
        pq.add(a)
        pq.add(c)

        class collector3(PythonCollector):
            def collect(_self, doc, score):
                self.assertEqual(1.0, score)
            def setNextReader(_self, context):
                pass
            def acceptsDocsOutOfOrder(_self):
                return True

        searcher.search(pq, collector3())

        pq.setSlop(2)

        class collector4(PythonCollector):
            def collect(_self, doc, score):
                self.assertEqual(2.0, score)
            def setNextReader(_self, context):
                pass
            def acceptsDocsOutOfOrder(_self):
                return True

        searcher.search(pq, collector4())


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
