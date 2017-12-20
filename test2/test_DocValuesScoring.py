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

from java.lang import Float

from org.apache.lucene.analysis.core import SimpleAnalyzer
from org.apache.lucene.document import \
    Document, Field, TextField, FloatDocValuesField
from org.apache.lucene.index import \
    DocValues, FieldInvertState, IndexReader, LeafReaderContext, Term
from org.apache.lucene.search import TermQuery
from org.apache.pylucene.search.similarities import \
    PythonPerFieldSimilarityWrapper, PythonSimilarity
from org.apache.lucene.store import Directory
from org.apache.lucene.util import BytesRef

#
# Tests the use of indexdocvalues in scoring.
#
# In the example, a docvalues field is used as a per-document boost (separate
# from the norm)
#

SCORE_EPSILON = 0.001  # for comparing floats


#
# Similarity that wraps another similarity and boosts the final score
# according to whats in a docvalues field.
#
class BoostingSimilarity(PythonSimilarity):
    def __init__(self, sim, boostField):
        super(BoostingSimilarity, self).__init__()
        self.sim = sim
        self.boostField = boostField

    def computeNorm(self, state):
        return self.sim.computeNorm(state)

    def computeWeight(self, boost, collectionStats, termStats):
        return self.sim.computeWeight(boost, collectionStats, termStats)

    def simScorer(self, stats, context):
        sub = self.sim.simScorer(stats, context)
        values = DocValues.getNumeric(context.reader(), self.boostField)

        class _SimScorer(PythonSimilarity.PythonSimScorer):
            def getValueForDoc(_self, doc):
                curDocID = values.docID()
                if doc < curDocID:
                    raise ValueError("doc=" + doc + " is before curDocID=" + curDocID)
                if doc > curDocID:
                    curDocID = values.advance(doc)

                if curDocID == doc:
                    return Float.intBitsToFloat(int(values.longValue()))
                else:
                    return 0.0

            def score(_self, doc, freq):
                return _self.getValueForDoc(doc) * sub.score(doc, freq)

        return _SimScorer()


class TestDocValuesScoring(PyLuceneTestCase):

    def testSimple(self):
        writer = self.getWriter(analyzer=SimpleAnalyzer())

        doc = Document()
        field = Field("foo", "", TextField.TYPE_NOT_STORED)
        doc.add(field)

        dvField = FloatDocValuesField("foo_boost", 0.0)
        doc.add(dvField)

        field2 = Field("bar", "", TextField.TYPE_NOT_STORED)
        doc.add(field2)

        field.setStringValue("quick brown fox")
        field2.setStringValue("quick brown fox")
        dvField.setFloatValue(2.0)  # boost x2
        writer.addDocument(doc)

        field.setStringValue("jumps over lazy brown dog")
        field2.setStringValue("jumps over lazy brown dog")
        dvField.setFloatValue(4.0)  # boost x4
        writer.addDocument(doc)

        reader = writer.getReader()
        writer.close()

        # no boosting
        searcher1 = self.getSearcher(reader=reader)
        base = searcher1.getSimilarity(True)

        # boosting
        searcher2 = self.getSearcher(reader=reader)

        class _similarity(PythonPerFieldSimilarityWrapper):

            def __init__(_self, base):
                super(_similarity, _self).__init__()
                _self.base = base
                _self.fooSim = BoostingSimilarity(base, "foo_boost")

            def get(_self, field):
                return _self.fooSim if "foo" == field else _self.base

        searcher2.setSimilarity(_similarity(base))

        # in this case, we searched on field "foo". first document should have
        # 2x the score.
        tq = TermQuery(Term("foo", "quick"))
        noboost = searcher1.search(tq, 10)
        boost = searcher2.search(tq, 10)

        self.assertEqual(1, noboost.totalHits)
        self.assertEqual(1, boost.totalHits)

        self.assertEqual(
            boost.scoreDocs[0].score, noboost.scoreDocs[0].score * 2.0,
            SCORE_EPSILON)

        # this query matches only the second document, which should have 4x
        # the score.
        tq = TermQuery(Term("foo", "jumps"))
        noboost = searcher1.search(tq, 10)
        boost = searcher2.search(tq, 10)
        self.assertEqual(1, noboost.totalHits)
        self.assertEqual(1, boost.totalHits)

        self.assertEqual(
            boost.scoreDocs[0].score, noboost.scoreDocs[0].score * 4.0,
            SCORE_EPSILON)

        # search on on field bar just for kicks, nothing should happen, since
        # we setup our sim provider to only use foo_boost for field foo.
        tq = TermQuery(Term("bar", "quick"))
        noboost = searcher1.search(tq, 10)
        boost = searcher2.search(tq, 10)
        self.assertEqual(1, noboost.totalHits)
        self.assertEqual(1, boost.totalHits)

        self.assertEqual(
            boost.scoreDocs[0].score, noboost.scoreDocs[0].score,
            SCORE_EPSILON)

        reader.close()


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
