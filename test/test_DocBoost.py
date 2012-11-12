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

from unittest import TestCase, main
from PyLuceneTestCase import PyLuceneTestCase

from org.apache.lucene.analysis.core import SimpleAnalyzer
from org.apache.lucene.document import Document, TextField
from org.apache.lucene.index import Term
from org.apache.lucene.search import TermQuery
from org.apache.pylucene.search import PythonCollector
from org.apache.lucene.util import Version


class DocBoostTestCase(PyLuceneTestCase):
    """
    Unit tests ported from Java Lucene
    """
  
    def testDocBoost(self):

        writer = self.getWriter(analyzer=SimpleAnalyzer(Version.LUCENE_CURRENT))
    
        f1 = self.newField("field", "word", TextField.TYPE_STORED)
        f2 = self.newField("field", "word", TextField.TYPE_STORED)
        f2.setBoost(2.0)
    
        d1 = Document()
        d2 = Document()
    
        d1.add(f1)                                 # boost = 1
        d2.add(f2)                                 # boost = 2
    
        writer.addDocument(d1)
        writer.addDocument(d2)
        writer.close()

        scores = [0.0] * 2

        class collector(PythonCollector):
            def __init__(_self, scores):
                super(collector, _self).__init__()
                _self.scores = scores
                _self.base = 0
            def collect(_self, doc, score):
                _self.scores[doc + _self.base] = score
            def setNextReader(_self, context):
                _self.base = context.docBase
            def acceptsDocsOutOfOrder(_self):
                return True

        self.getSearcher().search(TermQuery(Term("field", "word")),
                                  collector(scores))
    
        lastScore = 0.0
        for score in scores:
            self.assert_(score > lastScore)
            lastScore = score


if __name__ == "__main__":
    import sys, lucene
    lucene.initVM()
    if '-loop' in sys.argv:
        sys.argv.remove('-loop')
        while True:
            try:
                main()
            except:
                pass
    else:
         main()
