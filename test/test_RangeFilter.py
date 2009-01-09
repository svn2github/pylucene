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
        writer = IndexWriter(self.index, SimpleAnalyzer(), True)

        seed(101)
        for d in xrange(self.minId, self.maxId + 1):
            doc = Document()
            doc.add(Field("id", self.pad(d),
                          Field.Store.YES, Field.Index.UN_TOKENIZED))
            r = randint(~self.MAX_INT, self.MAX_INT)
            if self.maxR < r:
                self.maxR = r
            if r < self.minR:
                self.minR = r
            doc.add(Field("rand", self.pad(r),
                          Field.Store.YES, Field.Index.UN_TOKENIZED))
            doc.add(Field("body", "body",
                          Field.Store.YES, Field.Index.UN_TOKENIZED))
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

        reader = IndexReader.open(self.index);
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
                                              True, True))
        self.assertEqual(numDocs, result.length(), "find all")

        result = search.search(q, RangeFilter("id", minIP, maxIP,
                                              True, False))
        self.assertEqual(numDocs - 1, result.length(), "all but last")

        result = search.search(q, RangeFilter("id", minIP, maxIP,
                                              False, True))
        self.assertEqual(numDocs - 1, result.length(), "all but first")
        
        result = search.search(q, RangeFilter("id", minIP, maxIP,
                                              False, False))
        self.assertEqual(numDocs - 2, result.length(), "all but ends")
    
        result = search.search(q, RangeFilter("id", medIP, maxIP,
                                              True, True))
        self.assertEqual(1 + self.maxId - medId, result.length(), "med and up")
        
        result = search.search(q, RangeFilter("id", minIP, medIP,
                                              True, True))
        self.assertEqual(1 + medId - self.minId, result.length(), "up to med")

        # unbounded id

        result = search.search(q, RangeFilter("id", minIP, None,
                                              True, False))
        self.assertEqual(numDocs, result.length(), "min and up")

        result = search.search(q, RangeFilter("id", None, maxIP,
                                              False, True))
        self.assertEqual(numDocs, result.length(), "max and down")

        result = search.search(q, RangeFilter("id", minIP, None,
                                              False, False))
        self.assertEqual(numDocs - 1, result.length(), "not min, but up")
        
        result = search.search(q, RangeFilter("id", None, maxIP,
                                              False, False))
        self.assertEqual(numDocs - 1, result.length(), "not max, but down")
        
        result = search.search(q, RangeFilter("id",medIP, maxIP,
                                              True, False))
        self.assertEqual(self.maxId - medId, result.length(), "med and up, not max")
        
        result = search.search(q, RangeFilter("id", minIP, medIP,
                                              False, True))
        self.assertEqual(medId - self.minId, result.length(), "not min, up to med")

        # very small sets

        result = search.search(q, RangeFilter("id", minIP, minIP,
                                              False, False))
        self.assertEqual(0, result.length(), "min, min, False, False")

        result = search.search(q, RangeFilter("id", medIP, medIP,
                                              False, False))
        self.assertEqual(0, result.length(), "med, med, False, False")
        result = search.search(q, RangeFilter("id", maxIP, maxIP,
                                              False, False))
        self.assertEqual(0, result.length(), "max, max, False, False")
                     
        result = search.search(q, RangeFilter("id", minIP, minIP,
                                              True, True))
        self.assertEqual(1, result.length(), "min, min, True, True")
        result = search.search(q, RangeFilter("id", None, minIP,
                                              False, True))
        self.assertEqual(1, result.length(), "nul, min, False, True")

        result = search.search(q, RangeFilter("id", maxIP, maxIP,
                                              True, True))
        self.assertEqual(1, result.length(), "max, max, True, True")
        result = search.search(q, RangeFilter("id", maxIP, None,
                                              True, False))
        self.assertEqual(1, result.length(), "max, nul, True, True")

        result = search.search(q, RangeFilter("id", medIP, medIP,
                                              True, True))
        self.assertEqual(1, result.length(), "med, med, True, True")

    def testRangeFilterRand(self):

        reader = IndexReader.open(self.index)
        search = IndexSearcher(reader)

        minRP = self.pad(self.minR)
        maxRP = self.pad(self.maxR)

        numDocs = reader.numDocs()
        
        self.assertEqual(numDocs, 1 + self.maxId - self.minId, "num of docs")
        
        q = TermQuery(Term("body", "body"))

        # test extremes, bounded on both ends
        
        result = search.search(q, RangeFilter("rand", minRP, maxRP,
                                              True, True))
        self.assertEqual(numDocs, result.length(), "find all")

        result = search.search(q, RangeFilter("rand", minRP, maxRP,
                                              True, False))
        self.assertEqual(numDocs - 1, result.length(), "all but biggest")

        result = search.search(q, RangeFilter("rand", minRP, maxRP,
                                              False, True))
        self.assertEqual(numDocs - 1, result.length(), "all but smallest")
        
        result = search.search(q, RangeFilter("rand", minRP, maxRP,
                                              False, False))
        self.assertEqual(numDocs - 2, result.length(), "all but extremes")
    
        # unbounded

        result = search.search(q, RangeFilter("rand", minRP, None,
                                              True, False))
        self.assertEqual(numDocs, result.length(), "smallest and up")

        result = search.search(q, RangeFilter("rand", None, maxRP,
                                              False, True))
        self.assertEqual(numDocs, result.length(), "biggest and down")

        result = search.search(q, RangeFilter("rand", minRP, None,
                                              False, False))
        self.assertEqual(numDocs - 1, result.length(), "not smallest, but up")
        
        result = search.search(q, RangeFilter("rand", None, maxRP,
                                              False, False))
        self.assertEqual(numDocs - 1, result.length(), "not biggest, but down")
        
        # very small sets

        result = search.search(q, RangeFilter("rand", minRP, minRP,
                                              False, False))
        self.assertEqual(0, result.length(), "min, min, False, False")

        result = search.search(q, RangeFilter("rand", maxRP, maxRP,
                                              False, False))
        self.assertEqual(0, result.length(), "max, max, False, False")
                     
        result = search.search(q, RangeFilter("rand", minRP, minRP,
                                              True, True))
        self.assertEqual(1, result.length(), "min, min, True, True")

        result = search.search(q, RangeFilter("rand", None, minRP,
                                              False, True))
        self.assertEqual(1, result.length(), "nul, min, False, True")

        result = search.search(q, RangeFilter("rand", maxRP, maxRP,
                                              True, True))
        self.assertEqual(1, result.length(), "max, max, True, True")

        result = search.search(q, RangeFilter("rand", maxRP, None,
                                              True, False))
        self.assertEqual(1, result.length(), "max, nul, True, True")


if __name__ == "__main__":
    import sys, lucene
    lucene.initVM(lucene.CLASSPATH)
    if '-loop' in sys.argv:
        sys.argv.remove('-loop')
        while True:
            try:
                main(defaultTest='TestRangeFilter')
            except:
                pass
    else:
        main(defaultTest='TestRangeFilter')
