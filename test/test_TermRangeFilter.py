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
from BaseTestRangeFilter import BaseTestRangeFilter

from org.apache.lucene.analysis.core import SimpleAnalyzer
from org.apache.lucene.document import Document, Field, StringField
from org.apache.lucene.index import Term
from org.apache.lucene.store import RAMDirectory
from org.apache.lucene.search import TermQuery, TermRangeFilter

 #
 # A basic 'positive' Unit test class for the TermRangeFilter class.
 #
 # NOTE: at the moment, this class only tests for 'positive' results,
 # it does not verify the results to ensure there are no 'false positives',
 # nor does it adequately test 'negative' results.  It also does not test
 # that garbage in results in an Exception.
 #

def _trf(*args):
    return TermRangeFilter.newStringRange(*args)

class TestTermRangeFilter(BaseTestRangeFilter):

    def testRangeFilterId(self):

        index = self.signedIndex
        reader = self.getReader(directory=index.index);
        search = self.getSearcher(reader=reader)

        medId = ((self.maxId - self.minId) / 2)
        
        minIP = self.pad(self.minId)
        maxIP = self.pad(self.maxId)
        medIP = self.pad(medId)
    
        numDocs = reader.numDocs()
        
        self.assertEqual(numDocs, 1 + self.maxId - self.minId, "num of docs")
        
        q = TermQuery(Term("body","body"))

        # test id, bounded on both ends
        
        result = search.search(q, _trf("id", minIP, maxIP, True, True), 50)
        self.assertEqual(numDocs, result.totalHits, "find all")

        result = search.search(q, _trf("id", minIP, maxIP, True, False), 50)
        self.assertEqual(numDocs - 1, result.totalHits, "all but last")

        result = search.search(q, _trf("id", minIP, maxIP, False, True), 50)
        self.assertEqual(numDocs - 1, result.totalHits, "all but first")
        
        result = search.search(q, _trf("id", minIP, maxIP, False, False), 50)
        self.assertEqual(numDocs - 2, result.totalHits, "all but ends")
        
        result = search.search(q, _trf("id", medIP, maxIP, True, True), 50)
        self.assertEqual(1 + self.maxId - medId, result.totalHits, "med and up")
        
        result = search.search(q, _trf("id", minIP, medIP, True, True), 50)
        self.assertEqual(1 + medId - self.minId, result.totalHits, "up to med")

        # unbounded id

        result = search.search(q, _trf("id", minIP, None, True, False), 50)
        self.assertEqual(numDocs, result.totalHits, "min and up")
        
        result = search.search(q, _trf("id", None, maxIP, False, True), 50)
        self.assertEqual(numDocs, result.totalHits, "max and down")
        
        result = search.search(q, _trf("id", minIP, None, False, False), 50)
        self.assertEqual(numDocs - 1, result.totalHits, "not min, but up")
        
        result = search.search(q, _trf("id", None, maxIP, False, False), 50)
        self.assertEqual(numDocs - 1, result.totalHits, "not max, but down")
        
        result = search.search(q, _trf("id",medIP, maxIP, True, False), 50)
        self.assertEqual(self.maxId - medId, result.totalHits, "med and up, not max")
        
        result = search.search(q, _trf("id", minIP, medIP, False, True), 50)
        self.assertEqual(medId - self.minId, result.totalHits, "not min, up to med")

        # very small sets

        result = search.search(q, _trf("id", minIP, minIP, False, False), 50)
        self.assertEqual(0, result.totalHits, "min, min, False, False")
        
        result = search.search(q, _trf("id", medIP, medIP, False, False), 50)
        self.assertEqual(0, result.totalHits, "med, med, False, False")
        result = search.search(q, _trf("id", maxIP, maxIP, False, False), 50)
        self.assertEqual(0, result.totalHits, "max, max, False, False")
        
        result = search.search(q, _trf("id", minIP, minIP, True, True), 50)
        self.assertEqual(1, result.totalHits, "min, min, True, True")
        result = search.search(q, _trf("id", None, minIP, False, True), 50)
        self.assertEqual(1, result.totalHits, "nul, min, False, True")
        
        result = search.search(q, _trf("id", maxIP, maxIP, True, True), 50)
        self.assertEqual(1, result.totalHits, "max, max, True, True")
        result = search.search(q, _trf("id", maxIP, None, True, False), 50)
        self.assertEqual(1, result.totalHits, "max, nul, True, True")
        
        result = search.search(q, _trf("id", medIP, medIP, True, True), 50)
        self.assertEqual(1, result.totalHits, "med, med, True, True")
        
    def testRangeFilterRand(self):

        index = self.signedIndex
        reader = self.getReader(directory=index.index)
        search = self.getSearcher(reader=reader)

        minRP = self.pad(index.minR)
        maxRP = self.pad(index.maxR)

        numDocs = reader.numDocs()
        
        self.assertEqual(numDocs, 1 + self.maxId - self.minId, "num of docs")
        
        q = TermQuery(Term("body", "body"))

        # test extremes, bounded on both ends
        
        result = search.search(q, _trf("rand", minRP, maxRP, True, True), 50)
        self.assertEqual(numDocs, result.totalHits, "find all")

        result = search.search(q, _trf("rand", minRP, maxRP, True, False), 50)
        self.assertEqual(numDocs - 1, result.totalHits, "all but biggest")

        result = search.search(q, _trf("rand", minRP, maxRP, False, True), 50)
        self.assertEqual(numDocs - 1, result.totalHits, "all but smallest")
        
        result = search.search(q, _trf("rand", minRP, maxRP, False, False), 50)
        self.assertEqual(numDocs - 2, result.totalHits, "all but extremes")
    
        # unbounded

        result = search.search(q, _trf("rand", minRP, None, True, False), 50)
        self.assertEqual(numDocs, result.totalHits, "smallest and up")

        result = search.search(q, _trf("rand", None, maxRP, False, True), 50)
        self.assertEqual(numDocs, result.totalHits, "biggest and down")

        result = search.search(q, _trf("rand", minRP, None, False, False), 50)
        self.assertEqual(numDocs - 1, result.totalHits, "not smallest, but up")
        
        result = search.search(q, _trf("rand", None, maxRP, False, False), 50)
        self.assertEqual(numDocs - 1, result.totalHits, "not biggest, but down")
        
        # very small sets

        result = search.search(q, _trf("rand", minRP, minRP, False, False), 50)
        self.assertEqual(0, result.totalHits, "min, min, False, False")

        result = search.search(q, _trf("rand", maxRP, maxRP, False, False), 50)
        self.assertEqual(0, result.totalHits, "max, max, False, False")
                     
        result = search.search(q, _trf("rand", minRP, minRP, True, True), 50)
        self.assertEqual(1, result.totalHits, "min, min, True, True")

        result = search.search(q, _trf("rand", None, minRP, False, True), 50)
        self.assertEqual(1, result.totalHits, "nul, min, False, True")

        result = search.search(q, _trf("rand", maxRP, maxRP, True, True), 50)
        self.assertEqual(1, result.totalHits, "max, max, True, True")

        result = search.search(q, _trf("rand", maxRP, None, True, False), 50)
        self.assertEqual(1, result.totalHits, "max, nul, True, True")



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
