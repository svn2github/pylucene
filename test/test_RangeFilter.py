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

from random import seed, randint
from unittest import TestCase, main

from lucene import \
     SimpleAnalyzer, Document, Field, IndexWriter, RAMDirectory, \
     IndexReader, IndexSearcher, Term, TermQuery, RangeFilter


class BaseTestRangeFilter(TestCase):

    def __init__(self, *args):

        super(BaseTestRangeFilter, self).__init__(*args)

        self.index = RAMDirectory()

        self.MAX_INT = 0x7fffffff
        self.maxR = ~self.MAX_INT
        self.minR = self.MAX_INT
    
        self.minId = 0
        self.maxId = 10000

        self.build()

    #
    # a simple padding function that should work with any int
    #

    def pad(self, n):

        if n < 0:
            return "-%0.10d" % (self.MAX_INT + n + 1)
        else:
            return "0%0.10d" % n

    def build(self):

        # build an index
        writer = IndexWriter(self.index, SimpleAnalyzer(), True,
                             IndexWriter.MaxFieldLength.LIMITED)

        seed(101)
        for d in xrange(self.minId, self.maxId + 1):
            doc = Document()
            doc.add(Field("id", self.pad(d),
                          Field.Store.YES, Field.Index.NOT_ANALYZED))
            r = randint(~self.MAX_INT, self.MAX_INT)
            if self.maxR < r:
                self.maxR = r
            if r < self.minR:
                self.minR = r
            doc.add(Field("rand", self.pad(r),
                          Field.Store.YES, Field.Index.NOT_ANALYZED))
            doc.add(Field("body", "body",
                          Field.Store.YES, Field.Index.NOT_ANALYZED))
            writer.addDocument(doc)
            
        writer.optimize()
        writer.close()

    def testPad(self):

        tests = [-9999999, -99560, -100, -3, -1, 0, 3, 9, 10, 1000, 999999999]

        for i in xrange(0, len(tests) - 1):
            a = tests[i]
            b = tests[i + 1]
            aa = self.pad(a)
            bb = self.pad(b)
            label = "%s:%s vs %s:%s" %(a, aa, b, bb)
            self.assertEqual(len(aa), len(bb), "length of %s" %label)
            self.assert_(aa < bb, "compare less than %s" %label)


 #
 # A basic 'positive' Unit test class for the RangeFilter class.
 #
 # NOTE: at the moment, this class only tests for 'positive' results,
 # it does not verify the results to ensure there are no 'false positives',
 # nor does it adequately test 'negative' results.  It also does not test
 # that garbage in results in an Exception.
 #

class TestRangeFilter(BaseTestRangeFilter):

    def testRangeFilterId(self):

        reader = IndexReader.open(self.index, True);
        search = IndexSearcher(reader)

        medId = ((self.maxId - self.minId) / 2)
        
        minIP = self.pad(self.minId)
        maxIP = self.pad(self.maxId)
        medIP = self.pad(medId)
    
        numDocs = reader.numDocs()
        
        self.assertEqual(numDocs, 1 + self.maxId - self.minId, "num of docs")
        
        q = TermQuery(Term("body","body"))

        # test id, bounded on both ends
        
        result = search.search(q, RangeFilter("id", minIP, maxIP,
                                              True, True), 50)
        self.assertEqual(numDocs, result.totalHits, "find all")

        result = search.search(q, RangeFilter("id", minIP, maxIP,
                                              True, False), 50)
        self.assertEqual(numDocs - 1, result.totalHits, "all but last")

        result = search.search(q, RangeFilter("id", minIP, maxIP,
                                              False, True), 50)
        self.assertEqual(numDocs - 1, result.totalHits, "all but first")
        
        result = search.search(q, RangeFilter("id", minIP, maxIP,
                                              False, False), 50)
        self.assertEqual(numDocs - 2, result.totalHits, "all but ends")
    
        result = search.search(q, RangeFilter("id", medIP, maxIP,
                                              True, True), 50)
        self.assertEqual(1 + self.maxId - medId, result.totalHits, "med and up")
        
        result = search.search(q, RangeFilter("id", minIP, medIP,
                                              True, True), 50)
        self.assertEqual(1 + medId - self.minId, result.totalHits, "up to med")

        # unbounded id

        result = search.search(q, RangeFilter("id", minIP, None,
                                              True, False), 50)
        self.assertEqual(numDocs, result.totalHits, "min and up")

        result = search.search(q, RangeFilter("id", None, maxIP,
                                              False, True), 50)
        self.assertEqual(numDocs, result.totalHits, "max and down")

        result = search.search(q, RangeFilter("id", minIP, None,
                                              False, False), 50)
        self.assertEqual(numDocs - 1, result.totalHits, "not min, but up")
        
        result = search.search(q, RangeFilter("id", None, maxIP,
                                              False, False), 50)
        self.assertEqual(numDocs - 1, result.totalHits, "not max, but down")
        
        result = search.search(q, RangeFilter("id",medIP, maxIP,
                                              True, False), 50)
        self.assertEqual(self.maxId - medId, result.totalHits, "med and up, not max")
        
        result = search.search(q, RangeFilter("id", minIP, medIP,
                                              False, True), 50)
        self.assertEqual(medId - self.minId, result.totalHits, "not min, up to med")

        # very small sets

        result = search.search(q, RangeFilter("id", minIP, minIP,
                                              False, False), 50)
        self.assertEqual(0, result.totalHits, "min, min, False, False")

        result = search.search(q, RangeFilter("id", medIP, medIP,
                                              False, False), 50)
        self.assertEqual(0, result.totalHits, "med, med, False, False")
        result = search.search(q, RangeFilter("id", maxIP, maxIP,
                                              False, False), 50)
        self.assertEqual(0, result.totalHits, "max, max, False, False")
                     
        result = search.search(q, RangeFilter("id", minIP, minIP,
                                              True, True), 50)
        self.assertEqual(1, result.totalHits, "min, min, True, True")
        result = search.search(q, RangeFilter("id", None, minIP,
                                              False, True), 50)
        self.assertEqual(1, result.totalHits, "nul, min, False, True")

        result = search.search(q, RangeFilter("id", maxIP, maxIP,
                                              True, True), 50)
        self.assertEqual(1, result.totalHits, "max, max, True, True")
        result = search.search(q, RangeFilter("id", maxIP, None,
                                              True, False), 50)
        self.assertEqual(1, result.totalHits, "max, nul, True, True")

        result = search.search(q, RangeFilter("id", medIP, medIP,
                                              True, True), 50)
        self.assertEqual(1, result.totalHits, "med, med, True, True")

    def testRangeFilterRand(self):

        reader = IndexReader.open(self.index, True)
        search = IndexSearcher(reader)

        minRP = self.pad(self.minR)
        maxRP = self.pad(self.maxR)

        numDocs = reader.numDocs()
        
        self.assertEqual(numDocs, 1 + self.maxId - self.minId, "num of docs")
        
        q = TermQuery(Term("body", "body"))

        # test extremes, bounded on both ends
        
        result = search.search(q, RangeFilter("rand", minRP, maxRP,
                                              True, True), 50)
        self.assertEqual(numDocs, result.totalHits, "find all")

        result = search.search(q, RangeFilter("rand", minRP, maxRP,
                                              True, False), 50)
        self.assertEqual(numDocs - 1, result.totalHits, "all but biggest")

        result = search.search(q, RangeFilter("rand", minRP, maxRP,
                                              False, True), 50)
        self.assertEqual(numDocs - 1, result.totalHits, "all but smallest")
        
        result = search.search(q, RangeFilter("rand", minRP, maxRP,
                                              False, False), 50)
        self.assertEqual(numDocs - 2, result.totalHits, "all but extremes")
    
        # unbounded

        result = search.search(q, RangeFilter("rand", minRP, None,
                                              True, False), 50)
        self.assertEqual(numDocs, result.totalHits, "smallest and up")

        result = search.search(q, RangeFilter("rand", None, maxRP,
                                              False, True), 50)
        self.assertEqual(numDocs, result.totalHits, "biggest and down")

        result = search.search(q, RangeFilter("rand", minRP, None,
                                              False, False), 50)
        self.assertEqual(numDocs - 1, result.totalHits, "not smallest, but up")
        
        result = search.search(q, RangeFilter("rand", None, maxRP,
                                              False, False), 50)
        self.assertEqual(numDocs - 1, result.totalHits, "not biggest, but down")
        
        # very small sets

        result = search.search(q, RangeFilter("rand", minRP, minRP,
                                              False, False), 50)
        self.assertEqual(0, result.totalHits, "min, min, False, False")

        result = search.search(q, RangeFilter("rand", maxRP, maxRP,
                                              False, False), 50)
        self.assertEqual(0, result.totalHits, "max, max, False, False")
                     
        result = search.search(q, RangeFilter("rand", minRP, minRP,
                                              True, True), 50)
        self.assertEqual(1, result.totalHits, "min, min, True, True")

        result = search.search(q, RangeFilter("rand", None, minRP,
                                              False, True), 50)
        self.assertEqual(1, result.totalHits, "nul, min, False, True")

        result = search.search(q, RangeFilter("rand", maxRP, maxRP,
                                              True, True), 50)
        self.assertEqual(1, result.totalHits, "max, max, True, True")

        result = search.search(q, RangeFilter("rand", maxRP, None,
                                              True, False), 50)
        self.assertEqual(1, result.totalHits, "max, nul, True, True")


if __name__ == "__main__":
    import sys, lucene
    lucene.initVM()
    if '-loop' in sys.argv:
        sys.argv.remove('-loop')
        while True:
            try:
                main(defaultTest='TestRangeFilter')
            except:
                pass
    else:
        main(defaultTest='TestRangeFilter')
