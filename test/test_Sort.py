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

import re

from unittest import TestCase, main
from lucene import *


class SortTestCase(TestCase):
    """
    Unit tests for sorting code, ported from Java Lucene
    """

    # document data:
    # the tracer field is used to determine which document was hit
    # the contents field is used to search and sort by relevance
    # the int field to sort by int
    # the float field to sort by float
    # the string field to sort by string

    data = [
    #     tracer  contents          int           float          string  custom
        [   "A",   "x a",           "5",           "4f",           "c",   "A-3"   ],
        [   "B",   "y a",           "5",           "3.4028235E38", "i",   "B-10"  ],
        [   "C",   "x a b c",       "2147483647",  "1.0",          "j",   "A-2"   ],
        [   "D",   "y a b c",       "-1",          "0.0f",         "a",   "C-0"   ],
        [   "E",   "x a b c d",     "5",           "2f",           "h",   "B-8"   ],
        [   "F",   "y a b c d",     "2",           "3.14159f",     "g",   "B-1"   ],
        [   "G",   "x a b c d",     "3",           "-1.0",         "f",   "C-100" ],
        [   "H",   "y a b c d",     "0",           "1.4E-45",      "e",   "C-88"  ],
        [   "I",   "x a b c d e f", "-2147483648", "1.0e+0",       "d",   "A-10"  ],
        [   "J",   "y a b c d e f", "4",           ".5",           "b",   "C-7"   ],
	[   "W",   "g",             "1",           None,           None,  None    ],
	[   "X",   "g",             "1",           "0.1",          None,  None    ],
	[   "Y",   "g",             "1",           "0.2",          None,  None    ],
	[   "Z",   "f g",           None,          None,           None,  None    ]
        ]


    def _getIndex(self, even, odd):
        """
        Create an index of all the documents, or just the x,
        or just the y documents
        """
        
        indexStore = RAMDirectory()
        writer = IndexWriter(indexStore, SimpleAnalyzer(), True)

        for i in xrange(0, len(self.data)):
            if i % 2 == 0 and even or i % 2 == 1 and odd:
                doc = Document()
                doc.add(Field("tracer", self.data[i][0],
                              Field.Store.YES, Field.Index.NO))
                doc.add(Field("contents", self.data[i][1],
                              Field.Store.NO, Field.Index.TOKENIZED))
                if self.data[i][2] is not None:
                    doc.add(Field("int", self.data[i][2],
                                  Field.Store.NO, Field.Index.UN_TOKENIZED))
                if self.data[i][3] is not None:
                    doc.add(Field("float", self.data[i][3],
                                  Field.Store.NO, Field.Index.UN_TOKENIZED))
                if self.data[i][4] is not None:
                    doc.add(Field("string", self.data[i][4],
                                  Field.Store.NO, Field.Index.UN_TOKENIZED))
                if self.data[i][5] is not None:
                    doc.add(Field("custom", self.data[i][5],
                                  Field.Store.NO, Field.Index.UN_TOKENIZED))
                writer.addDocument(doc)

        writer.optimize()
        writer.close()

        return IndexSearcher(indexStore)

    def _getFullIndex(self):
        return self._getIndex(True, True)

    def _getXIndex(self):
        return self._getIndex(True, False)

    def _getYIndex(self):
        return self._getIndex(False, True)

    def _getEmptyIndex(self):
        return self._getIndex(False, False)

    def _assertMatches(self, searcher, query, sort, expectedResult):
        """
        Make sure the documents returned by the search match the expected list
        """
        
        buff = ''.join([''.join(Hit.cast_(hit).getDocument().getValues("tracer"))
                        for hit in searcher.search(query, sort)])

        self.assertEqual(expectedResult, buff)

    def _assertMatchesPattern(self, searcher, query, sort, pattern):
        """
        make sure the documents returned by the search match the expected
        list pattern
        """

        buff = ''.join([''.join(Hit.cast_(hit).getDocument().getValues("tracer"))
                        for hit in searcher.search(query, sort)])

        self.assert_(re.compile(pattern).match(buff))

    def _getComparatorSource(self):
        return self._getComparator()

    def _getComparable(self, termtext):

        class comparable(PythonComparable):
            def __init__(self, termText):
                super(comparable, self).__init__()
                self.string_part, self.int_part = termText.split('-')
                self.int_part = int(self.int_part)
            def compareTo(self, o):
                return (cmp(self.string_part, o.string_part) or
                        cmp(self.int_part, o.int_part))

        return comparable(termtext)

    def _getComparator(self):

        class comparator(PythonSortComparator):

            def getComparable(_self, termText):
                return self._getComparable(termText)

            def newComparator(_self, reader, fieldname):
                 enumerator = reader.terms(Term(fieldname, ""))

                 class comparator(PythonScoreDocComparator):
                     def __init__(_self, cache):
                         super(comparator, _self).__init__()
                         _self.cache = cache
                     def compare(_self, i, j):
                         return _self.cache[i.doc].compareTo(_self.cache[j.doc])
                     def sortType(_self):
                         return SortField.CUSTOM
                     def sortValue(_self, i):
                         return _self.cache[i.doc]

                 try:
                     cache = self._fillCache(reader, enumerator, fieldname)
                     return comparator(cache)
                 finally:
                     enumerator.close()

        return comparator()

    def _fillCache(self, reader, enumerator, fieldName):
        """
        Returns an array of objects which represent that natural order
        of the term values in the given field.

        @param reader     Terms are in this index.
        @param enumerator Use this to get the term values and TermDocs.
        @param fieldname  Comparables should be for this field.
        @return Array of objects representing natural order of terms in field.
        """

        retArray = [None] * reader.maxDoc()
        if len(retArray) > 0:
            termDocs = reader.termDocs()
            try:
                if enumerator.term() is None:
                    raise RuntimeError, "no terms in field " + fieldName
                while True:
                    term = enumerator.term()
                    if term.field() != fieldName:
                        break
                    termval = self._getComparable(term.text())
                    termDocs.seek(enumerator)
                    while termDocs.next():
                        retArray[termDocs.doc()] = termval
                    if not enumerator.next():
                        break
            finally:
                termDocs.close()

        return retArray

    def _runMultiSorts(self, multi):
        """
        runs a variety of sorts useful for multisearchers
        """

        sort = Sort()

        sort.setSort(SortField.FIELD_DOC)
        self._assertMatchesPattern(multi, self.queryA, sort,
                                   "[AB]{2}[CD]{2}[EF]{2}[GH]{2}[IJ]{2}")

        sort.setSort(SortField("int", SortField.INT))
        self._assertMatchesPattern(multi, self.queryA, sort,
                                   "IDHFGJ[ABE]{3}C")
        
        sort.setSort([SortField("int", SortField.INT),
                      SortField.FIELD_DOC])
        self._assertMatchesPattern(multi, self.queryA, sort,
                                   "IDHFGJ[AB]{2}EC")

        sort.setSort("int")
        self._assertMatchesPattern(multi, self.queryA, sort,
                                   "IDHFGJ[AB]{2}EC")

        sort.setSort([SortField("float", SortField.FLOAT),
                      SortField.FIELD_DOC])
        self._assertMatchesPattern(multi, self.queryA, sort,
                                   "GDHJ[CI]{2}EFAB")

        sort.setSort("float")
        self._assertMatchesPattern(multi, self.queryA, sort,
                                   "GDHJ[CI]{2}EFAB")

        sort.setSort("string")
        self._assertMatches(multi, self.queryA, sort, "DJAIHGFEBC")

        sort.setSort("int", True)
        self._assertMatchesPattern(multi, self.queryA, sort,
                                   "C[AB]{2}EJGFHDI")

        sort.setSort("float", True)
        self._assertMatchesPattern(multi, self.queryA, sort,
                                   "BAFE[IC]{2}JHDG")

        sort.setSort("string", True)
        self._assertMatches(multi, self.queryA, sort, "CBEFGHIAJD")

        sort.setSort([SortField("string", Locale.US)])
        self._assertMatches(multi, self.queryA, sort, "DJAIHGFEBC")

        sort.setSort([SortField("string", Locale.US, True)])
        self._assertMatches(multi, self.queryA, sort, "CBEFGHIAJD")

        sort.setSort(["int", "float"])
        self._assertMatches(multi, self.queryA, sort, "IDHFGJEABC")

        sort.setSort(["float", "string"])
        self._assertMatches(multi, self.queryA, sort, "GDHJICEFAB")

        sort.setSort("int")
        self._assertMatches(multi, self.queryF, sort, "IZJ")

        sort.setSort("int", True)
        self._assertMatches(multi, self.queryF, sort, "JZI")

        sort.setSort("float")
        self._assertMatches(multi, self.queryF, sort, "ZJI")

        sort.setSort("string")
        self._assertMatches(multi, self.queryF, sort, "ZJI")

        sort.setSort("string", True)
        self._assertMatches(multi, self.queryF, sort, "IJZ")

    def _getScores(self, hits):

        scoreMap = {}

        for hit in hits:
            hit = Hit.cast_(hit)
            doc = hit.getDocument()
            v = doc.getValues("tracer")
            self.assertEqual(len(v), 1)
            scoreMap[v[0]] = float(hit.getScore())

        return scoreMap

    def _assertSameValues(self, m1, m2):
        """
        make sure all the values in the maps match
        """

        n = len(m1)
        m = len(m2)
        self.assertEqual(n, m)

        for key in m1.iterkeys():
            self.assertEqual(m1[key], m2[key])

    def setUp(self):

        self.full = self._getFullIndex()
        self.searchX = self._getXIndex()
        self.searchY = self._getYIndex()
        self.queryX = TermQuery(Term("contents", "x"))
        self.queryY = TermQuery(Term("contents", "y"))
        self.queryA = TermQuery(Term("contents", "a"))
        self.queryF = TermQuery(Term("contents", "f"))

    def tearDown(self):
        
        del self.full
        del self.queryX
        del self.queryY
        del self.queryA
        del self.queryF
        del self.searchX
        del self.searchY

    def testBuiltInSorts(self):
        """
        test the sorts by score and document number
        """

        sort = Sort()
        self._assertMatches(self.full, self.queryX, sort, "ACEGI")
        self._assertMatches(self.full, self.queryY, sort, "BDFHJ")

        sort.setSort(SortField.FIELD_DOC)
        self._assertMatches(self.full, self.queryX, sort, "ACEGI")
        self._assertMatches(self.full, self.queryY, sort, "BDFHJ")

    def testTypedSort(self):
        """
        test sorts where the type of field is specified
        """

        sort = Sort()
        sort.setSort([SortField("int", SortField.INT),
                      SortField.FIELD_DOC])
        self._assertMatches(self.full, self.queryX, sort, "IGAEC")
        self._assertMatches(self.full, self.queryY, sort, "DHFJB")

        sort.setSort([SortField("float", SortField.FLOAT),
                      SortField.FIELD_DOC])
        self._assertMatches(self.full, self.queryX, sort, "GCIEA")
        self._assertMatches(self.full, self.queryY, sort, "DHJFB")

        sort.setSort([SortField("string", SortField.STRING),
                      SortField.FIELD_DOC])
        self._assertMatches(self.full, self.queryX, sort, "AIGEC")
        self._assertMatches(self.full, self.queryY, sort, "DJHFB")


    def testEmptyIndex(self):
        """
        test sorts when there's nothing in the index
        """

        sort = Sort()
        empty = self._getEmptyIndex()

        self._assertMatches(empty, self.queryX, sort, "")

        sort.setSort(SortField.FIELD_DOC)
        self._assertMatches(empty, self.queryX, sort, "")

        sort.setSort([SortField("int", SortField.INT),
                      SortField.FIELD_DOC])
        self._assertMatches(empty, self.queryX, sort, "")

        sort.setSort([SortField("string", SortField.STRING, True),
                      SortField.FIELD_DOC])
        self._assertMatches(empty, self.queryX, sort, "")

        sort.setSort([SortField("float", SortField.FLOAT),
                      SortField("string", SortField.STRING)])
        self._assertMatches(empty, self.queryX, sort, "")


    def testAutoSort(self):
        """
        test sorts where the type of field is determined dynamically
        """

        sort = Sort()

        sort.setSort("int")
        self._assertMatches(self.full, self.queryX, sort, "IGAEC")
        self._assertMatches(self.full, self.queryY, sort, "DHFJB")

        sort.setSort("float")
        self._assertMatches(self.full, self.queryX, sort, "GCIEA")
        self._assertMatches(self.full, self.queryY, sort, "DHJFB")

        sort.setSort("string")
        self._assertMatches(self.full, self.queryX, sort, "AIGEC")
        self._assertMatches(self.full, self.queryY, sort, "DJHFB")

    def testReverseSort(self):
        """
        test sorts in reverse
        """

        sort = Sort()

        sort.setSort([SortField(None, SortField.SCORE, True),
                      SortField.FIELD_DOC])
        self._assertMatches(self.full, self.queryX, sort, "IEGCA")
        self._assertMatches(self.full, self.queryY, sort, "JFHDB")

        sort.setSort(SortField(None, SortField.DOC, True))
        self._assertMatches(self.full, self.queryX, sort, "IGECA")
        self._assertMatches(self.full, self.queryY, sort, "JHFDB")

        sort.setSort("int", True)
        self._assertMatches(self.full, self.queryX, sort, "CAEGI")
        self._assertMatches(self.full, self.queryY, sort, "BJFHD")

        sort.setSort("float", True)
        self._assertMatches(self.full, self.queryX, sort, "AECIG")
        self._assertMatches(self.full, self.queryY, sort, "BFJHD")

        sort.setSort("string", True)
        self._assertMatches(self.full, self.queryX, sort, "CEGIA")
        self._assertMatches(self.full, self.queryY, sort, "BFHJD")

    def testEmptyFieldSort(self):
        """
        test sorting when the sort field is empty (undefined)
        for some of the documents
        """

        sort = Sort()
        
        sort.setSort("string")
        self._assertMatches(self.full, self.queryF, sort, "ZJI")

        sort.setSort("string", True)
        self._assertMatches(self.full, self.queryF, sort, "IJZ")

        sort.setSort("int")
        self._assertMatches(self.full, self.queryF, sort, "IZJ")

        sort.setSort("int", True)
        self._assertMatches(self.full, self.queryF, sort, "JZI")

        sort.setSort("float")
        self._assertMatches(self.full, self.queryF, sort, "ZJI")

        sort.setSort("float", True)
        self._assertMatches(self.full, self.queryF, sort, "IJZ")
        
    def testSortCombos(self):
        """
        test sorts using a series of fields
        """

        sort = Sort()
        
        sort.setSort(["int", "float"])
        self._assertMatches(self.full, self.queryX, sort, "IGEAC")

        sort.setSort([SortField("int", True),
                      SortField(None, SortField.DOC, True)])
        self._assertMatches(self.full, self.queryX, sort, "CEAGI")

        sort.setSort(["float", "string"])
        self._assertMatches(self.full, self.queryX, sort, "GICEA")

    def testLocaleSort(self):
        """
        test using a Locale for sorting strings
        """

        sort = Sort()
        
        sort.setSort([SortField("string", Locale.US)])
        self._assertMatches(self.full, self.queryX, sort, "AIGEC")
        self._assertMatches(self.full, self.queryY, sort, "DJHFB")

        sort.setSort([SortField("string", Locale.US, True)])
        self._assertMatches(self.full, self.queryX, sort, "CEGIA")
        self._assertMatches(self.full, self.queryY, sort, "BFHJD")

    def testCustomSorts(self):
        """
        test a custom sort function
        """

        sort = Sort()
        
        sort.setSort(SortField("custom", self._getComparatorSource()))
        self._assertMatches(self.full, self.queryX, sort, "CAIEG")

        sort.setSort(SortField("custom", self._getComparatorSource(), True))
        self._assertMatches(self.full, self.queryY, sort, "HJDBF")

        custom = self._getComparator()
        sort.setSort(SortField("custom", custom))
        self._assertMatches(self.full, self.queryX, sort, "CAIEG")

        sort.setSort(SortField("custom", custom, True))
        self._assertMatches(self.full, self.queryY, sort, "HJDBF")

    def testMultiSort(self):
        """
        test a variety of sorts using more than one searcher
        """
         
        searcher = MultiSearcher([self.searchX, self.searchY])
        self._runMultiSorts(searcher)

    def testParallelMultiSort(self):
        """
        test a variety of sorts using a parallel multisearcher
        """

        searcher = ParallelMultiSearcher([self.searchX, self.searchY])
        self._runMultiSorts(searcher)

    def testNormalizedScores(self):
        """
        test that the relevancy scores are the same even if
        hits are sorted
        """

        full = self.full

        # capture relevancy scores
        scoresX = self._getScores(full.search(self.queryX))
        scoresY = self._getScores(full.search(self.queryY))
        scoresA = self._getScores(full.search(self.queryA))

        # we'll test searching locally and multi
        # note: the multi test depends on each separate index containing
        # the same documents as our local index, so the computed normalization
        # will be the same.  so we make a multi searcher over two equal document
        # sets - not realistic, but necessary for testing.

        queryX = self.queryX
        queryY = self.queryY
        queryA = self.queryA

        multi = MultiSearcher([self.searchX, self.searchY])

        gs = self._getScores

        # change sorting and make sure relevancy stays the same

        sort = Sort()

        self._assertSameValues(scoresX, gs(full.search(queryX, sort)))
        self._assertSameValues(scoresX, gs(multi.search(queryX, sort)))
        self._assertSameValues(scoresY, gs(full.search(queryY, sort)))
        self._assertSameValues(scoresY, gs(multi.search(queryY, sort)))
        self._assertSameValues(scoresA, gs(full.search(queryA, sort)))
        self._assertSameValues(scoresA, gs(multi.search(queryA, sort)))

        sort.setSort(SortField.FIELD_DOC)
        self._assertSameValues(scoresX, gs(full.search(queryX,sort)))
        self._assertSameValues(scoresX, gs(multi.search(queryX, sort)))
        self._assertSameValues(scoresY, gs(full.search(queryY, sort)))
        self._assertSameValues(scoresY, gs(multi.search(queryY, sort)))
        self._assertSameValues(scoresA, gs(full.search(queryA, sort)))
        self._assertSameValues(scoresA, gs(multi.search(queryA, sort)))

        sort.setSort("int")
        self._assertSameValues(scoresX, gs(full.search(queryX, sort)))
        self._assertSameValues(scoresX, gs(multi.search(queryX, sort)))
        self._assertSameValues(scoresY, gs(full.search(queryY, sort)))
        self._assertSameValues(scoresY, gs(multi.search(queryY, sort)))
        self._assertSameValues(scoresA, gs(full.search(queryA, sort)))
        self._assertSameValues(scoresA, gs(multi.search(queryA, sort)))

        sort.setSort("float")
        self._assertSameValues(scoresX, gs(full.search(queryX, sort)))
        self._assertSameValues(scoresX, gs(multi.search(queryX, sort)))
        self._assertSameValues(scoresY, gs(full.search(queryY, sort)))
        self._assertSameValues(scoresY, gs(multi.search(queryY, sort)))
        self._assertSameValues(scoresA, gs(full.search(queryA, sort)))
        self._assertSameValues(scoresA, gs(multi.search(queryA, sort)))

        sort.setSort("string")
        self._assertSameValues(scoresX, gs(full.search(queryX, sort)))
        self._assertSameValues(scoresX, gs(multi.search(queryX, sort)))
        self._assertSameValues(scoresY, gs(full.search(queryY, sort)))
        self._assertSameValues(scoresY, gs(multi.search(queryY, sort)))
        self._assertSameValues(scoresA, gs(full.search(queryA, sort)))
        self._assertSameValues(scoresA, gs(multi.search(queryA, sort)))

        sort.setSort(["int", "float"])
        self._assertSameValues(scoresX, gs(full.search(queryX, sort)))
        self._assertSameValues(scoresX, gs(multi.search(queryX, sort)))
        self._assertSameValues(scoresY, gs(full.search(queryY, sort)))
        self._assertSameValues(scoresY, gs(multi.search(queryY, sort)))
        self._assertSameValues(scoresA, gs(full.search(queryA, sort)))
        self._assertSameValues(scoresA, gs(multi.search(queryA, sort)))

        sort.setSort([SortField("int", True),
                      SortField(None, SortField.DOC, True)])
        self._assertSameValues(scoresX, gs(full.search(queryX, sort)))
        self._assertSameValues(scoresX, gs(multi.search(queryX, sort)))
        self._assertSameValues(scoresY, gs(full.search(queryY, sort)))
        self._assertSameValues(scoresY, gs(multi.search(queryY, sort)))
        self._assertSameValues(scoresA, gs(full.search(queryA, sort)))
        self._assertSameValues(scoresA, gs(multi.search(queryA, sort)))

        sort.setSort(["float", "string"])
        self._assertSameValues(scoresX, gs(full.search(queryX, sort)))
        self._assertSameValues(scoresX, gs(multi.search(queryX, sort)))
        self._assertSameValues(scoresY, gs(full.search(queryY, sort)))
        self._assertSameValues(scoresY, gs(multi.search(queryY, sort)))
        self._assertSameValues(scoresA, gs(full.search(queryA, sort)))
        self._assertSameValues(scoresA, gs(multi.search(queryA, sort)))


if __name__ == "__main__":
    import sys, lucene
    env = lucene.initVM(lucene.CLASSPATH)
    if '-loop' in sys.argv:
        sys.argv.remove('-loop')
        while True:
            try:
                main()
            except:
                pass
#            refs = sorted(env._dumpRefs(classes=True).items(),
#                          key=lambda x: x[1], reverse=True)
#            print refs[0:4]
    else:
        main()
