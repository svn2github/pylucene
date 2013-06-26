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

import sys, lucene, unittest, math
from PyLuceneTestCase import PyLuceneTestCase

from itertools import izip
from random import randint

from java.lang import Byte, Double, Float, Integer, Long, Short
from java.util import BitSet
from java.util.concurrent import Executors, TimeUnit
from org.apache.lucene.analysis.core import SimpleAnalyzer
from org.apache.lucene.codecs import Codec
from org.apache.lucene.document import \
    Document, Field, FieldType, StringField, StoredField, TextField, \
    NumericDocValuesField, SortedDocValuesField, BinaryDocValuesField, \
    FloatDocValuesField
from org.apache.lucene.index import \
    FieldInfo, LogDocMergePolicy, MultiReader, Term
from org.apache.lucene.search import \
    BooleanQuery, BooleanClause, FieldCache, IndexSearcher, MatchAllDocsQuery, Sort, \
    SortField, TermQuery, TopFieldCollector
from org.apache.lucene.store import RAMDirectory
from org.apache.lucene.util import \
    BytesRef, DocIdBitSet, FieldCacheSanityChecker, NamedThreadFactory, Version
from org.apache.pylucene.search import \
    PythonIntParser, PythonFloatParser, PythonLongParser, PythonDoubleParser, \
    PythonByteParser, PythonShortParser, \
    PythonFieldComparator, PythonFieldComparatorSource, PythonFilter

NUM_STRINGS = 750


class SortTestCase(PyLuceneTestCase):
    """
    Unit tests for sorting code, ported from Java Lucene
    """

    def __init__(self, *args, **kwds):

        super(SortTestCase, self).__init__(*args, **kwds)
        self.supportsDocValues = Codec.getDefault().getName() > "Lucene3x"

        self.data = [
            # tracer  contents         int            float           string   custom   i18n               long            double,          short,     byte, 'custom parser encoding'
            [ "A",   "x a",           "5",           "4f",           "c",     "A-3",   "p\u00EAche",      "10",           "-4.0",            "3",    "126", "J" ],  # A, x
            [ "B",   "y a",           "5",           "3.4028235E38", "i",     "B-10",  "HAT",             "1000000000",   "40.0",           "24",      "1", "I" ],  # B, y
            [ "C",   "x a b c",       "2147483647",  "1.0",          "j",     "A-2",   "p\u00E9ch\u00E9", "99999999","40.00002343",        "125",     "15", "H" ],  # C, x
            [ "D",   "y a b c",       "-1",          "0.0f",         "a",     "C-0",   "HUT",   str(Long.MAX_VALUE), str(Double.MIN_VALUE), str(Short.MIN_VALUE), str(Byte.MIN_VALUE), "G" ], # D, y
            [ "E",   "x a b c d",     "5",           "2f",           "h",     "B-8",   "peach", str(Long.MIN_VALUE), str(Double.MAX_VALUE), str(Short.MAX_VALUE), str(Byte.MAX_VALUE), "F" ], # E, x
            [ "F",   "y a b c d",     "2",           "3.14159f",     "g",     "B-1",   "H\u00C5T",        "-44",          "343.034435444",  "-3",      "0", "E" ],  # F, y
            [ "G",   "x a b c d",     "3",           "-1.0",         "f",     "C-100", "sin",             "323254543543", "4.043544",        "5",    "100", "D" ],  # G, x
            [ "H",   "y a b c d",     "0",           "1.4E-45",      "e",     "C-88",  "H\u00D8T",        "1023423423005","4.043545",       "10",    "-50", "C" ],  # H, y
            [ "I",   "x a b c d e f", "-2147483648", "1.0e+0",       "d",     "A-10",  "s\u00EDn",        "332422459999", "4.043546",     "-340",     "51", "B" ],  # I, x
            [ "J",   "y a b c d e f", "4",           ".5",           "b",     "C-7",   "HOT",             "34334543543",  "4.0000220343",  "300",      "2", "A" ],  # J, y
            [ "W",   "g",             "1",           None,           None,    None,    None,              None,           None,             None,     None, None ],
            [ "X",   "g",             "1",           "0.1",          None,    None,    None,              None,           None,             None,     None, None ],
            [ "Y",   "g",             "1",           "0.2",          None,    None,    None,              None,           None,             None,     None, None ],
            [ "Z",   "f g",           None,          None,           None,    None,    None,              None,           None,             None,     None, None ],
  
            # Sort Missing first/last
            [ "a",   "m",             None,          None,           None,    None,    None,              None,           None,             None,     None, None ],
            [ "b",   "m",            "4",           "4.0",           "4",     None,    None,              "4",            "4",               "4",      "4", None ],
            [ "c",   "m",            "5",           "5.0",           "5",     None,    None,              "5",            "5",               "5",      "5", None ],
            [ "d",   "m",            None,           None,           None,    None,    None,              None,           None,             None,     None, None ],
        ]

    def setUp(self):
        super(SortTestCase, self).setUp()

        self.dirs = []
        self.dvStringSorted = self.getRandomBoolean()

        # run the randomization at setup so that threads share it and we don't
        # hit cache incompatibilities
        self.notSorted = self.getRandomBoolean()
        # If you index as sorted source you can still sort by value instead:
        self.sortByValue = self.getRandomBoolean()

        self.full = self._getFullIndex()
        self.searchX = self._getXIndex()
        self.searchY = self._getYIndex()
        self.queryX = TermQuery(Term("contents", "x"))
        self.queryY = TermQuery(Term("contents", "y"))
        self.queryA = TermQuery(Term("contents", "a"))
        self.queryE = TermQuery(Term("contents", "e"))
        self.queryF = TermQuery(Term("contents", "f"))
        self.queryG = TermQuery(Term("contents", "g"))
        self.queryM = TermQuery(Term("contents", "m"))
        self.sort = Sort()

    def tearDown(self):

        for directory in self.dirs:
            directory.close()

        super(SortTestCase, self).tearDown()

    def _getIndex(self, even, odd):

        mergePolicy = LogDocMergePolicy()
        mergePolicy.setMergeFactor(1000)
        directory = RAMDirectory()
        self.dirs.append(directory)

        writer = self.getWriter(directory=directory,
                                analyzer=SimpleAnalyzer(Version.LUCENE_CURRENT),
                                maxBufferedDocs=2, mergePolicy=mergePolicy)

        if self.dvStringSorted:
            # Index sorted
            stringDVType = FieldInfo.DocValuesType.SORTED
        elif self.notSorted:
            # Index non-sorted
            stringDVType = FieldInfo.DocValuesType.BINARY
        else:
            # sorted anyway
            stringDVType = FieldInfo.DocValuesType.SORTED

        ft1 = FieldType()
        ft1.setStored(True)
        ft2 = FieldType()
        ft2.setIndexed(True)

        for i in xrange(len(self.data)):
            if (i % 2 == 0 and even) or (i % 2 == 1 and odd):
                doc = Document()
                doc.add(Field("tracer", self.data[i][0], ft1))
                doc.add(TextField("contents", self.data[i][1], Field.Store.NO))
                if self.data[i][2] is not None:
                    doc.add(StringField("int", self.data[i][2], Field.Store.NO))
                    if self.supportsDocValues:
                        doc.add(NumericDocValuesField("int_dv", Long.parseLong(self.data[i][2])))
                if self.data[i][3] is not None:
                    doc.add(StringField("float", self.data[i][3], Field.Store.NO))
                    if self.supportsDocValues:
                        doc.add(FloatDocValuesField("float_dv", Float.parseFloat(self.data[i][3])))

                if self.data[i][4] is not None:
                    doc.add(StringField("string", self.data[i][4], Field.Store.NO))
                    if self.supportsDocValues:
                        if stringDVType == FieldInfo.DocValuesType.SORTED:
                            doc.add(SortedDocValuesField("string_dv", BytesRef(self.data[i][4])))
                        elif stringDVType == FieldInfo.DocValuesType.BINARY:
                            doc.add(BinaryDocValuesField("string_dv", BytesRef(self.data[i][4])))
                        else:
                            raise ValueError("unknown type " + stringDVType)

                if self.data[i][5] is not None:
                    doc.add(StringField("custom", self.data[i][5], Field.Store.NO))
                if self.data[i][6] is not None:
                    doc.add(StringField("i18n", self.data[i][6], Field.Store.NO))
                if self.data[i][7] is not None:
                    doc.add(StringField("long", self.data[i][7], Field.Store.NO))
                if self.data[i][8] is not None:
                    doc.add(StringField("double", self.data[i][8], Field.Store.NO))
                    if self.supportsDocValues:
                        doc.add(NumericDocValuesField("double_dv", Double.doubleToRawLongBits(Double.parseDouble(self.data[i][8]))))
                if self.data[i][9] is not None:
                    doc.add(StringField("short", self.data[i][9], Field.Store.NO))
                if self.data[i][10] is not None:
                    doc.add(StringField("byte", self.data[i][10], Field.Store.NO))
                if self.data[i][11] is not None:
                    doc.add(StringField("parser", self.data[i][11], Field.Store.NO))

                for f in doc.getFields():
                    if f.fieldType().indexed() and not f.fieldType().omitNorms():
                        Field.cast_(f).setBoost(2.0)

                writer.addDocument(doc)

        reader = writer.getReader()
        writer.close()

        return self.getSearcher(reader=reader)

    def _getFullIndex(self):
        return self._getIndex(True, True)

    def _getFullStrings(self):

        mergePolicy = LogDocMergePolicy()
        mergePolicy.setMergeFactor(97)
        directory = RAMDirectory()
        self.dirs.append(directory)

        writer = self.getWriter(directory=directory,
                                analyzer=SimpleAnalyzer(Version.LUCENE_CURRENT),
                                maxBufferedDocs=4, mergePolicy=mergePolicy)
        
        onlyStored = FieldType()
        onlyStored.setStored(True)
        fixedLen = self.getRandomNumber(2, 8)
        fixedLen2 = self.getRandomNumber(1, 4)

        for i in xrange(NUM_STRINGS):
            doc = Document()

            num = self.getRandomCharString(self.getRandomNumber(2, 8), 48, 52)
            doc.add(Field("tracer", num, onlyStored))
            doc.add(StringField("string", num, Field.Store.NO))
            if self.supportsDocValues:
                if self.dvStringSorted:
                    doc.add(SortedDocValuesField("string_dv", BytesRef(num)))
                else:
                    doc.add(BinaryDocValuesField("string_dv", BytesRef(num)))

            num2 = self.getRandomCharString(self.getRandomNumber(1, 4), 48, 50)
            doc.add(StringField("string2", num2, Field.Store.NO))
            if self.supportsDocValues:
                if self.dvStringSorted:
                    doc.add(SortedDocValuesField("string2_dv", BytesRef(num2)))
                else:
                    doc.add(BinaryDocValuesField("string2_dv", BytesRef(num2)))
            doc.add(Field("tracer2", num2, onlyStored))
            for f2 in doc.getFields():
                if f2.fieldType().indexed() and not f2.fieldType().omitNorms():
                    Field.cast_(f2).setBoost(2.0)

            numFixed = self.getRandomCharString(fixedLen, 48, 52)
            doc.add(Field("fixed_tracer", numFixed, onlyStored))
            doc.add(StringField("string_fixed", numFixed, Field.Store.NO))
            if self.supportsDocValues:
                if self.dvStringSorted:
                    doc.add(SortedDocValuesField("string_fixed_dv", BytesRef(numFixed)))
                else:
                    doc.add(BinaryDocValuesField("string_fixed_dv", BytesRef(numFixed)))

            num2Fixed = self.getRandomCharString(fixedLen2, 48, 52)
            doc.add(StringField("string2_fixed", num2Fixed, Field.Store.NO))
            if self.supportsDocValues:
                if self.dvStringSorted:
                    doc.add(SortedDocValuesField("string2_fixed_dv", BytesRef(num2Fixed)))
                else:
                    doc.add(BinaryDocValuesField("string2_fixed_dv", BytesRef(num2Fixed)))
            doc.add(Field("tracer2_fixed", num2Fixed, onlyStored))
            for f2 in doc.getFields():
                if f2.fieldType().indexed() and not f2.fieldType().omitNorms():
                    Field.cast_(f2).setBoost(2.0)

            writer.addDocument(doc)

        writer.close()

        return self.getSearcher(directory=directory)
  
    def getRandomNumberString(self, num, low, high):

        return ''.join([self.getRandomNumber(low, high) for i in xrange(num)])
  
    def getRandomCharString(self, num):

        return self.getRandomCharString(num, 48, 122)
  
    def getRandomCharString(self, num,  start, end):
        
        return ''.join([chr(self.getRandomNumber(start, end))
                        for i in xrange(num)])
  
    def getRandomNumber(self, low, high):
  
        return randint(low, high)

    def getRandomBoolean(self):
  
        return randint(0, 1) == 1

    def _getXIndex(self):
        return self._getIndex(True, False)

    def _getYIndex(self):
        return self._getIndex(False, True)

    def _getEmptyIndex(self):
        return self._getIndex(False, False)

    def testBuiltInSorts(self):
        """
        test the sorts by score and document number
        """

        sort = self.sort
        self._assertMatches(self.full, self.queryX, sort, "ACEGI")
        self._assertMatches(self.full, self.queryY, sort, "BDFHJ")

        sort.setSort(SortField.FIELD_DOC)
        self._assertMatches(self.full, self.queryX, sort, "ACEGI")
        self._assertMatches(self.full, self.queryY, sort, "BDFHJ")

    def testTypedSort(self):
        """
        test sorts where the type of field is specified
        """
        sort = self.sort

        sort.setSort([SortField("int", SortField.Type.INT), SortField.FIELD_DOC])
        self._assertMatches(self.full, self.queryX, sort, "IGAEC")
        self._assertMatches(self.full, self.queryY, sort, "DHFJB")

        sort.setSort([SortField("float", SortField.Type.FLOAT),
                      SortField.FIELD_DOC])
        self._assertMatches(self.full, self.queryX, sort, "GCIEA")
        self._assertMatches(self.full, self.queryY, sort, "DHJFB")

        sort.setSort([SortField("long", SortField.Type.LONG),
                      SortField.FIELD_DOC])
        self._assertMatches(self.full, self.queryX, sort, "EACGI")
        self._assertMatches(self.full, self.queryY, sort, "FBJHD")

        sort.setSort([SortField("double", SortField.Type.DOUBLE),
                      SortField.FIELD_DOC])
        self._assertMatches(self.full, self.queryX, sort, "AGICE")
        self._assertMatches(self.full, self.queryY, sort, "DJHBF")

        sort.setSort([SortField("byte", SortField.Type.BYTE),
                      SortField.FIELD_DOC])
        self._assertMatches(self.full, self.queryX, sort, "CIGAE")
        self._assertMatches(self.full, self.queryY, sort, "DHFBJ")

        sort.setSort([SortField("short", SortField.Type.SHORT),
                      SortField.FIELD_DOC])
        self._assertMatches(self.full, self.queryX, sort, "IAGCE")
        self._assertMatches(self.full, self.queryY, sort, "DFHBJ")

        sort.setSort([SortField("string", SortField.Type.STRING),
                      SortField.FIELD_DOC])
        self._assertMatches(self.full, self.queryX, sort, "AIGEC")
        self._assertMatches(self.full, self.queryY, sort, "DJHFB")

        if self.supportsDocValues:
            sort.setSort([SortField("int_dv", SortField.Type.INT),
                          SortField.FIELD_DOC])
            self._assertMatches(self.full, self.queryX, sort, "IGAEC")
            self._assertMatches(self.full, self.queryY, sort, "DHFJB")

            sort.setSort([SortField("float_dv", SortField.Type.FLOAT),
                          SortField.FIELD_DOC])
            self._assertMatches(self.full, self.queryX, sort, "GCIEA")
            self._assertMatches(self.full, self.queryY, sort, "DHJFB")
      
            sort.setSort([SortField("double_dv", SortField.Type.DOUBLE),
                          SortField.FIELD_DOC])
            self._assertMatches(self.full, self.queryX, sort, "AGICE")
            self._assertMatches(self.full, self.queryY, sort, "DJHBF")

            sort.setSort([SortField("string_dv", self._getDVStringSortType()),
                          SortField.FIELD_DOC])
            self._assertMatches(self.full, self.queryX, sort, "AIGEC")
            self._assertMatches(self.full, self.queryY, sort, "DJHFB")
  
    def _getDVStringSortType(self, allowSorted=True):

        if self.dvStringSorted and allowSorted:
            if self.sortByValue:
                return SortField.Type.STRING_VAL
            else:
                return SortField.Type.STRING
        else:
            return SortField.Type.STRING_VAL

    def _verifyStringSort(self, sort):

        searcher = self._getFullStrings()
        result = searcher.search(MatchAllDocsQuery(), None,
                                 self.getRandomNumber(500, searcher.getIndexReader().maxDoc()),
                                 sort).scoreDocs

        buff = []
        n = len(result)
        last = None
        lastSub = None
        lastDocId = 0
        fail = False

        if "_fixed" in sort.getSort()[0].getField():
            fieldSuffix = "_fixed"
        else:
            fieldSuffix = ""

        for scoreDoc in result:
            doc2 = searcher.doc(scoreDoc.doc)
            v = doc2.getValues("tracer" + fieldSuffix)
            v2 = doc2.getValues("tracer2" + fieldSuffix)
            for _v, _v2 in izip(v, v2):
                buff.append(_v + "(" + _v2 + ")(" + str(scoreDoc.doc) + ")\n")
                if last is not None:
                    _cmp = cmp(_v, last)
                    if _cmp < 0: # ensure first field is in order
                        fail = True
                        print "fail:", _v, "<", last
                        buff.append("  WRONG tracer\n")

                    if _cmp == 0: # ensure second field is in reverse order
                        _cmp = cmp(_v2, lastSub)
                        if _cmp > 0:
                            fail = True
                            print "rev field fail:", _v2, ">", lastSub
                            buff.append("  WRONG tracer2\n")
                        elif _cmp == 0: # ensure docid is in order
                            if scoreDoc.doc < lastDocId:
                                fail = True
                                print "doc fail:", scoreDoc.doc, ">", lastDocId
                                buff.append("  WRONG docID\n")
                last = _v
                lastSub = _v2
                lastDocId = scoreDoc.doc

        if fail:
            print "topn field1(field2)(docID):", ''.join(buff)

        self.assert_(not fail, "Found sort results out of order")
        searcher.getIndexReader().close()
  
    def testStringSort(self):
        """
        Test String sorting: small queue to many matches, multi field sort,
        reverse sort
        """

        sort = self.sort

        # Normal string field, var length
        sort.setSort([SortField("string", SortField.Type.STRING),
                      SortField("string2", SortField.Type.STRING, True),
                      SortField.FIELD_DOC])
        self._verifyStringSort(sort)

        # Normal string field, fixed length
        sort.setSort([SortField("string_fixed", SortField.Type.STRING),
                      SortField("string2_fixed", SortField.Type.STRING, True),
                      SortField.FIELD_DOC])
        self._verifyStringSort(sort)

        # Doc values field, var length
        self.assertTrue(self.supportsDocValues, "cannot work with preflex codec")
        sort.setSort([SortField("string_dv", self._getDVStringSortType()),
                      SortField("string2_dv", self._getDVStringSortType(), True),
                      SortField.FIELD_DOC])
        self._verifyStringSort(sort)

        # Doc values field, fixed length
        sort.setSort([SortField("string_fixed_dv", self._getDVStringSortType()),
                      SortField("string2_fixed_dv", self._getDVStringSortType(), True),
                      SortField.FIELD_DOC])
        self._verifyStringSort(sort)

    def testCustomFieldParserSort(self):
        """
        test sorts where the type of field is specified and a custom field
        parser is used, that uses a simple char encoding. The sorted string
        contains a character beginning from 'A' that is mapped to a numeric
        value using some "funny" algorithm to be different for each data
        type.
        """

        # since tests explicitly use different parsers on the same field name
        # we explicitly check/purge the FieldCache between each assertMatch
        fc = FieldCache.DEFAULT
        
        class intParser(PythonIntParser):
            def parseInt(_self, val):
                return (val.bytes[val.offset] - ord('A')) * 123456
            def termsEnum(_self, terms):
                return terms.iterator(None)

        class floatParser(PythonFloatParser):
            def parseFloat(_self, val):
                return math.sqrt(val.bytes[val.offset])
            def termsEnum(_self, terms):
                return terms.iterator(None)

        class longParser(PythonLongParser):
            def parseLong(_self, val):
                return (val.bytes[val.offset] - ord('A')) * 1234567890L
            def termsEnum(_self, terms):
                return terms.iterator(None)

        class doubleParser(PythonDoubleParser):
            def parseDouble(_self, val):
                return math.pow(val.bytes[val.offset], val.bytes[val.offset] - ord('A'))
            def termsEnum(_self, terms):
                return terms.iterator(None)

        class byteParser(PythonByteParser):
            def parseByte(_self, val):
                return chr(val.bytes[val.offset] - ord('A'))
            def termsEnum(_self, terms):
                return terms.iterator(None)

        class shortParser(PythonShortParser):
            def parseShort(_self, val):
                return val.bytes[val.offset] - ord('A')
            def termsEnum(_self, terms):
                return terms.iterator(None)

        sort = self.sort

        sort.setSort([SortField("parser", intParser()),
                      SortField.FIELD_DOC])

        self._assertMatches(self.full, self.queryA, sort, "JIHGFEDCBA")
        self._assertSaneFieldCaches(self.getName() + " IntParser")
        fc.purgeAllCaches()

        sort.setSort([SortField("parser", floatParser()),
                      SortField.FIELD_DOC])
        self._assertMatches(self.full, self.queryA, sort, "JIHGFEDCBA")
        self._assertSaneFieldCaches(self.getName() + " FloatParser")
        fc.purgeAllCaches()

        sort.setSort([SortField("parser", longParser()),
                      SortField.FIELD_DOC])
        self._assertMatches(self.full, self.queryA, sort, "JIHGFEDCBA")
        self._assertSaneFieldCaches(self.getName() + " LongParser")
        fc.purgeAllCaches()

        sort.setSort([SortField("parser", doubleParser()),
                      SortField.FIELD_DOC])
        self._assertMatches(self.full, self.queryA, sort, "JIHGFEDCBA")
        self._assertSaneFieldCaches(self.getName() + " DoubleParser")
        fc.purgeAllCaches()

        sort.setSort([SortField("parser", byteParser()),
                      SortField.FIELD_DOC])
        self._assertMatches(self.full, self.queryA, sort, "JIHGFEDCBA")
        self._assertSaneFieldCaches(self.getName() + " ByteParser")
        fc.purgeAllCaches()

        sort.setSort([SortField("parser", shortParser()),
                      SortField.FIELD_DOC])
        self._assertMatches(self.full, self.queryA, sort, "JIHGFEDCBA")
        self._assertSaneFieldCaches(self.getName() + " ShortParser")
        fc.purgeAllCaches()

    def testEmptyIndex(self):
        """
        test sorts when there's nothing in the index
        """

        sort = self.sort
        empty = self._getEmptyIndex()

        self._assertMatches(empty, self.queryX, sort, "")

        sort.setSort(SortField.FIELD_DOC)
        self._assertMatches(empty, self.queryX, sort, "")

        sort.setSort([SortField("int", SortField.Type.INT),
                      SortField.FIELD_DOC])
        self._assertMatches(empty, self.queryX, sort, "")

        sort.setSort([SortField("int_dv", SortField.Type.INT),
                      SortField.FIELD_DOC])
        self._assertMatches(empty, self.queryX, sort, "")

        sort.setSort([SortField("string", SortField.Type.STRING, True),
                      SortField.FIELD_DOC])
        self._assertMatches(empty, self.queryX, sort, "")

        sort.setSort([SortField("float", SortField.Type.FLOAT),
                      SortField("string", SortField.Type.STRING)])
        self._assertMatches(empty, self.queryX, sort, "")

        sort.setSort([SortField("float_dv", SortField.Type.FLOAT),
                      SortField("string", SortField.Type.STRING)])
        self._assertMatches(empty, self.queryX, sort, "")

        sort.setSort([SortField("string_dv", self._getDVStringSortType(False),
                                True),
                      SortField.FIELD_DOC])
        self._assertMatches(empty, self.queryX, sort, "")

        sort.setSort([SortField("float_dv", SortField.Type.FLOAT),
                      SortField("string_dv", self._getDVStringSortType(False))])
        self._assertMatches(empty, self.queryX, sort, "")
    
        sort.setSort([SortField("float_dv", SortField.Type.FLOAT),
                      SortField("string_dv", self._getDVStringSortType(False))])
        self._assertMatches(empty, self.queryX, sort, "")

    def testNewCustomFieldParserSort(self):
        """
        Test sorting w/ custom FieldComparator
        """
        sort = self.sort

        sort.setSort([SortField("parser", MyFieldComparatorSource())])
        self._assertMatches(self.full, self.queryA, sort, "JIHGFEDCBA")

    def testReverseSort(self):
        """
        test sorts in reverse
        """
        sort = self.sort

        sort.setSort([SortField(None, SortField.Type.SCORE, True),
                      SortField.FIELD_DOC])
        self._assertMatches(self.full, self.queryX, sort, "IEGCA")
        self._assertMatches(self.full, self.queryY, sort, "JFHDB")

        sort.setSort(SortField(None, SortField.Type.DOC, True))
        self._assertMatches(self.full, self.queryX, sort, "IGECA")
        self._assertMatches(self.full, self.queryY, sort, "JHFDB")

        sort.setSort(SortField("int", SortField.Type.INT, True))
        self._assertMatches(self.full, self.queryX, sort, "CAEGI")
        self._assertMatches(self.full, self.queryY, sort, "BJFHD")

        sort.setSort(SortField("float", SortField.Type.FLOAT, True))
        self._assertMatches(self.full, self.queryX, sort, "AECIG")
        self._assertMatches(self.full, self.queryY, sort, "BFJHD")

        sort.setSort(SortField("string", SortField.Type.STRING, True))
        self._assertMatches(self.full, self.queryX, sort, "CEGIA")
        self._assertMatches(self.full, self.queryY, sort, "BFHJD")

        if self.supportsDocValues:
            sort.setSort(SortField("int_dv", SortField.Type.INT, True))
            self._assertMatches(self.full, self.queryX, sort, "CAEGI")
            self._assertMatches(self.full, self.queryY, sort, "BJFHD")
      
            sort.setSort(SortField("float_dv", SortField.Type.FLOAT, True))
            self._assertMatches(self.full, self.queryX, sort, "AECIG")
            self._assertMatches(self.full, self.queryY, sort, "BFJHD")
    
            sort.setSort(SortField("string_dv", self._getDVStringSortType(), True))
            self._assertMatches(self.full, self.queryX, sort, "CEGIA")
            self._assertMatches(self.full, self.queryY, sort, "BFHJD")

    def testEmptyFieldSort(self):
        """
        test sorting when the sort field is empty(undefined) for some of the
        documents
        """
        sort = self.sort

        sort.setSort(SortField("string", SortField.Type.STRING))
        self._assertMatches(self.full, self.queryF, sort, "ZJI")

        sort.setSort(SortField("string", SortField.Type.STRING, True))
        self._assertMatches(self.full, self.queryF, sort, "IJZ")
    
        sort.setSort(SortField("int", SortField.Type.INT))
        self._assertMatches(self.full, self.queryF, sort, "IZJ")

        sort.setSort(SortField("int", SortField.Type.INT, True))
        self._assertMatches(self.full, self.queryF, sort, "JZI")

        sort.setSort(SortField("float", SortField.Type.FLOAT))
        self._assertMatches(self.full, self.queryF, sort, "ZJI")

        # using a nonexisting field as first sort key shouldn't make a
        # difference:
        sort.setSort([SortField("nosuchfield", SortField.Type.STRING),
                      SortField("float", SortField.Type.FLOAT)])
        self._assertMatches(self.full, self.queryF, sort, "ZJI")

        sort.setSort(SortField("float", SortField.Type.FLOAT, True))
        self._assertMatches(self.full, self.queryF, sort, "IJZ")

        # When a field is None for both documents, the next SortField should
        # be used. 
        # Works for
        sort.setSort([SortField("int", SortField.Type.INT),
                      SortField("string", SortField.Type.STRING),
                      SortField("float", SortField.Type.FLOAT)])
        self._assertMatches(self.full, self.queryG, sort, "ZWXY")

        # Reverse the last criterium to make sure the test didn't pass by
        # chance 
        sort.setSort([SortField("int", SortField.Type.INT),
                      SortField("string", SortField.Type.STRING),
                      SortField("float", SortField.Type.FLOAT, True)])
        self._assertMatches(self.full, self.queryG, sort, "ZYXW")

        # Do the same for a ParallelMultiSearcher

        threadPool = Executors.newFixedThreadPool(self.getRandomNumber(2, 8), NamedThreadFactory("testEmptyFieldSort"))
        parallelSearcher=IndexSearcher(self.full.getIndexReader(), threadPool)

        sort.setSort([SortField("int", SortField.Type.INT),
                      SortField("string", SortField.Type.STRING),
                      SortField("float", SortField.Type.FLOAT)])
        self._assertMatches(parallelSearcher, self.queryG, sort, "ZWXY")

        sort.setSort([SortField("int", SortField.Type.INT),
                      SortField("string", SortField.Type.STRING),
                      SortField("float", SortField.Type.FLOAT, True)])
        self._assertMatches(parallelSearcher, self.queryG, sort, "ZYXW")

        threadPool.shutdown()
        threadPool.awaitTermination(1000L, TimeUnit.MILLISECONDS)

    def testSortCombos(self):
        """
        test sorts using a series of fields
        """
        sort = self.sort

        sort.setSort([SortField("int", SortField.Type.INT),
                      SortField("float", SortField.Type.FLOAT)])
        self._assertMatches(self.full, self.queryX, sort, "IGEAC")

        sort.setSort([SortField("int", SortField.Type.INT, True),
                      SortField(None, SortField.Type.DOC, True)])
        self._assertMatches(self.full, self.queryX, sort, "CEAGI")

        sort.setSort([SortField("float", SortField.Type.FLOAT),
                      SortField("string", SortField.Type.STRING)])
        self._assertMatches(self.full, self.queryX, sort, "GICEA")

        if self.supportsDocValues:
            sort.setSort([SortField("int_dv", SortField.Type.INT),
                          SortField("float_dv", SortField.Type.FLOAT)])
            self._assertMatches(self.full, self.queryX, sort, "IGEAC")

            sort.setSort([SortField("int_dv", SortField.Type.INT, True),
                          SortField(None, SortField.Type.DOC, True)])
            self._assertMatches(self.full, self.queryX, sort, "CEAGI")

            sort.setSort([SortField("float_dv", SortField.Type.FLOAT),
                          SortField("string_dv", self._getDVStringSortType())])
            self._assertMatches(self.full, self.queryX, sort, "GICEA")

    def testParallelMultiSort(self):
        """
        test a variety of sorts using a parallel multisearcher
        """
        threadPool = Executors.newFixedThreadPool(self.getRandomNumber(2, 8), NamedThreadFactory("testParallelMultiSort"))
        searcher = IndexSearcher(MultiReader([self.searchX.getIndexReader(),
                                              self.searchY.getIndexReader()]),
                                 threadPool)
        self._runMultiSorts(searcher, False)

        threadPool.shutdown();
        threadPool.awaitTermination(1000L, TimeUnit.MILLISECONDS);

    def testTopDocsScores(self):
        """
        There was previously a bug in FieldSortedHitQueue.maxscore when only
        a single doc was added.  That is what the following tests for.
        """
        
        sort = Sort()
        nDocs = 10

        # try to pick a query that will result in an unnormalized
        # score greater than 1 to test for correct normalization
        docs1 = self.full.search(self.queryE, None, nDocs, sort, True, True)

        # a filter that only allows through the first hit
        class filter(PythonFilter):
            def getDocIdSet(_self, context, acceptDocs):
                reader = context.reader()
                bs = BitSet(reader.maxDoc())
                bs.set(0, reader.maxDoc())
                bs.set(docs1.scoreDocs[0].doc)
                return DocIdBitSet(bs)

        docs2 = self.full.search(self.queryE, filter(), nDocs, sort, True, True)

        self.assertEqual(docs1.scoreDocs[0].score,
                         docs2.scoreDocs[0].score,
                         1e-6)
  
    def testSortWithoutFillFields(self):
        """
        There was previously a bug in TopFieldCollector when fillFields was
        set to False - the same doc and score was set in ScoreDoc[]
        array. This test asserts that if fillFields is False, the documents
        are set properly. It does not use Searcher's default search
        methods(with Sort) since all set fillFields to True.
        """

        sorts = [Sort(SortField.FIELD_DOC), Sort()]
        for sort in sorts:
            q = MatchAllDocsQuery()
            tdc = TopFieldCollector.create(sort, 10, False,
                                           False, False, True)
            self.full.search(q, tdc)
      
            sds = tdc.topDocs().scoreDocs
            for i in xrange(1, len(sds)):
                self.assert_(sds[i].doc != sds[i - 1].doc)

    def testSortWithoutScoreTracking(self):
        """
        Two Sort criteria to instantiate the multi/single comparators.
        """

        sorts = [Sort(SortField.FIELD_DOC), Sort()]
        for sort in sorts:
            q = MatchAllDocsQuery()
            tdc = TopFieldCollector.create(sort, 10, True, False,
                                           False, True)
      
            self.full.search(q, tdc)
      
            tds = tdc.topDocs()
            sds = tds.scoreDocs
            for sd in sds:
                self.assert_(Float.isNaN_(sd.score))

            self.assert_(Float.isNaN_(tds.getMaxScore()))

    def testSortWithScoreNoMaxScoreTracking(self):
        """
        Two Sort criteria to instantiate the multi/single comparators.
        """
        
        sorts = [Sort(SortField.FIELD_DOC), Sort()]
        for sort in sorts:
            q = MatchAllDocsQuery()
            tdc = TopFieldCollector.create(sort, 10, True, True,
                                           False, True)
      
            self.full.search(q, tdc)
      
            tds = tdc.topDocs()
            sds = tds.scoreDocs
            for sd in sds:
                self.assert_(not Float.isNaN_(sd.score))

            self.assert_(Float.isNaN_(tds.getMaxScore()))
  
    def testSortWithScoreAndMaxScoreTracking(self):
        """
        Two Sort criteria to instantiate the multi/single comparators.
        """
        
        sorts = [Sort(SortField.FIELD_DOC), Sort()]
        for sort in sorts:
            q = MatchAllDocsQuery()
            tdc = TopFieldCollector.create(sort, 10, True, True,
                                           True, True)
      
            self.full.search(q, tdc)
      
            tds = tdc.topDocs()
            sds = tds.scoreDocs
            for sd in sds:
                self.assert_(not Float.isNaN_(sd.score))

            self.assert_(not Float.isNaN_(tds.getMaxScore()))

    def testOutOfOrderDocsScoringSort(self):
        """
        Two Sort criteria to instantiate the multi/single comparators.
        """

        sorts = [Sort(SortField.FIELD_DOC), Sort()]

        tfcOptions = [[False, False, False],
                      [False, False, True],
                      [False, True, False],
                      [False, True, True],
                      [True, False, False],
                      [True, False, True],
                      [True, True, False],
                      [True, True, True]]

        actualTFCClasses = [
            "OutOfOrderOneComparatorNonScoringCollector", 
            "OutOfOrderOneComparatorScoringMaxScoreCollector", 
            "OutOfOrderOneComparatorScoringNoMaxScoreCollector", 
            "OutOfOrderOneComparatorScoringMaxScoreCollector", 
            "OutOfOrderOneComparatorNonScoringCollector", 
            "OutOfOrderOneComparatorScoringMaxScoreCollector", 
            "OutOfOrderOneComparatorScoringNoMaxScoreCollector", 
            "OutOfOrderOneComparatorScoringMaxScoreCollector" 
        ]
    
        bq = BooleanQuery()

        # Add a Query with SHOULD, since bw.scorer() returns BooleanScorer2
        # which delegates to BS if there are no mandatory clauses.
        bq.add(MatchAllDocsQuery(), BooleanClause.Occur.SHOULD)

        # Set minNrShouldMatch to 1 so that BQ will not optimize rewrite to
        # return the clause instead of BQ.
        bq.setMinimumNumberShouldMatch(1)

        for sort in sorts:
            for tfcOption, actualTFCClass in izip(tfcOptions,
                                                  actualTFCClasses):
                tdc = TopFieldCollector.create(sort, 10, tfcOption[0],
                                               tfcOption[1], tfcOption[2],
                                               False)

                self.assert_(tdc.getClass().getName().endswith("$" + actualTFCClass))
          
                self.full.search(bq, tdc)
          
                tds = tdc.topDocs()
                sds = tds.scoreDocs  
                self.assertEqual(10, len(sds))
  
    def testSortWithScoreAndMaxScoreTrackingNoResults(self):
        """
        Two Sort criteria to instantiate the multi/single comparators.
        """

        sorts = [Sort(SortField.FIELD_DOC), Sort()]
        for sort in sorts:
            tdc = TopFieldCollector.create(sort, 10, True, True, True, True)
            tds = tdc.topDocs()
            self.assertEqual(0, tds.totalHits)
            self.assert_(Float.isNaN_(tds.getMaxScore()))
  
    def _runMultiSorts(self, multi, isFull):
        """
        runs a variety of sorts useful for multisearchers
        """
        sort = self.sort

        sort.setSort(SortField.FIELD_DOC)
        expected = isFull and "ABCDEFGHIJ" or "ACEGIBDFHJ"
        self._assertMatches(multi, self.queryA, sort, expected)

        sort.setSort(SortField("int", SortField.Type.INT))
        expected = isFull and "IDHFGJABEC" or "IDHFGJAEBC"
        self._assertMatches(multi, self.queryA, sort, expected)

        sort.setSort([SortField("int", SortField.Type.INT), SortField.FIELD_DOC])
        expected = isFull and "IDHFGJABEC" or "IDHFGJAEBC"
        self._assertMatches(multi, self.queryA, sort, expected)

        sort.setSort(SortField("int", SortField.Type.INT))
        expected = isFull and "IDHFGJABEC" or "IDHFGJAEBC"
        self._assertMatches(multi, self.queryA, sort, expected)

        sort.setSort([SortField("float", SortField.Type.FLOAT), SortField.FIELD_DOC])
        self._assertMatches(multi, self.queryA, sort, "GDHJCIEFAB")

        sort.setSort(SortField("float", SortField.Type.FLOAT))
        self._assertMatches(multi, self.queryA, sort, "GDHJCIEFAB")

        sort.setSort(SortField("string", SortField.Type.STRING))
        self._assertMatches(multi, self.queryA, sort, "DJAIHGFEBC")

        sort.setSort(SortField("int", SortField.Type.INT, True))
        expected = isFull and "CABEJGFHDI" or "CAEBJGFHDI"
        self._assertMatches(multi, self.queryA, sort, expected)

        sort.setSort(SortField("float", SortField.Type.FLOAT, True))
        self._assertMatches(multi, self.queryA, sort, "BAFECIJHDG")

        sort.setSort(SortField("string", SortField.Type.STRING, True))
        self._assertMatches(multi, self.queryA, sort, "CBEFGHIAJD")

        sort.setSort([SortField("int", SortField.Type.INT),
                      SortField("float", SortField.Type.FLOAT)])
        self._assertMatches(multi, self.queryA, sort, "IDHFGJEABC")

        sort.setSort([SortField("float", SortField.Type.FLOAT),
                      SortField("string", SortField.Type.STRING)])
        self._assertMatches(multi, self.queryA, sort, "GDHJICEFAB")

        sort.setSort(SortField("int", SortField.Type.INT))
        self._assertMatches(multi, self.queryF, sort, "IZJ")

        sort.setSort(SortField("int", SortField.Type.INT, True))
        self._assertMatches(multi, self.queryF, sort, "JZI")

        sort.setSort(SortField("float", SortField.Type.FLOAT))
        self._assertMatches(multi, self.queryF, sort, "ZJI")

        sort.setSort(SortField("string", SortField.Type.STRING))
        self._assertMatches(multi, self.queryF, sort, "ZJI")

        sort.setSort(SortField("string", SortField.Type.STRING, True))
        self._assertMatches(multi, self.queryF, sort, "IJZ")

        if self.supportsDocValues:
            sort.setSort(SortField("int_dv", SortField.Type.INT))
            expected = isFull and "IDHFGJABEC" or "IDHFGJAEBC"
            self._assertMatches(multi, self.queryA, sort, expected)

            sort.setSort([SortField("int_dv", SortField.Type.INT),
                          SortField.FIELD_DOC])
            expected = isFull and "IDHFGJABEC" or "IDHFGJAEBC"
            self._assertMatches(multi, self.queryA, sort, expected)

            sort.setSort(SortField("int_dv", SortField.Type.INT))
            expected = isFull and "IDHFGJABEC" or "IDHFGJAEBC"
            self._assertMatches(multi, self.queryA, sort, expected)
    
            sort.setSort([SortField("float_dv", SortField.Type.FLOAT),
                          SortField.FIELD_DOC])
            self._assertMatches(multi, self.queryA, sort, "GDHJCIEFAB")

            sort.setSort(SortField("float_dv", SortField.Type.FLOAT))
            self._assertMatches(multi, self.queryA, sort, "GDHJCIEFAB")

            sort.setSort(SortField("int_dv", SortField.Type.INT, True))
            expected = isFull and "CABEJGFHDI" or "CAEBJGFHDI"
            self._assertMatches(multi, self.queryA, sort, expected)

            sort.setSort([SortField("int_dv", SortField.Type.INT),
                          SortField("float_dv", SortField.Type.FLOAT)])
            self._assertMatches(multi, self.queryA, sort, "IDHFGJEABC")

            sort.setSort(SortField("int_dv", SortField.Type.INT))
            self._assertMatches(multi, self.queryF, sort, "IZJ")

            sort.setSort(SortField("int_dv", SortField.Type.INT, True))
            self._assertMatches(multi, self.queryF, sort, "JZI")

            sort.setSort(SortField("string_dv", self._getDVStringSortType()))
            self._assertMatches(multi, self.queryA, sort, "DJAIHGFEBC")

            sort.setSort(SortField("string_dv", self._getDVStringSortType(), True))
            self._assertMatches(multi, self.queryA, sort, "CBEFGHIAJD")

            sort.setSort([SortField("float_dv", SortField.Type.FLOAT),
                          SortField("string_dv", self._getDVStringSortType())])
            self._assertMatches(multi, self.queryA, sort, "GDHJICEFAB")

            sort.setSort(SortField("string_dv", self._getDVStringSortType()))
            self._assertMatches(multi, self.queryF, sort, "ZJI")

            sort.setSort(SortField("string_dv", self._getDVStringSortType(), True))
            self._assertMatches(multi, self.queryF, sort, "IJZ")

        # up to this point, all of the searches should have "sane" 
        # FieldCache behavior, and should have reused hte cache in several
        # cases 
        self._assertSaneFieldCaches(self.getName() + " various")
        FieldCache.DEFAULT.purgeAllCaches()

    def _assertMatches(self, searcher, query, sort, expectedResult):
        """
        make sure the documents returned by the search match the expected
        list
        """

        # ScoreDoc[] result = searcher.search(query, None, 1000, sort).scoreDocs
        hits = searcher.search(query, None, len(expectedResult) or 1, sort)
        sds = hits.scoreDocs

        self.assertEqual(hits.totalHits, len(expectedResult))
        buff = []
        for sd in sds:
            doc = searcher.doc(sd.doc)
            v = doc.getValues("tracer")
            for _v in v:
                buff.append(_v)

        self.assertEqual(expectedResult, ''.join(buff))

    def getScores(self, hits, searcher):

        scoreMap = {}
        for hit in hits:
            doc = searcher.doc(hit.doc)
            v = doc.getValues("tracer")
            self.assertEqual(len(v), 1)
            scoreMap[v[0]] = hit.score

        return scoreMap

    def _assertSameValues(self, m1, m2):
        """
        make sure all the values in the maps match
        """

        self.assertEquals(len(m1), len(m2))
        for key in m1.iterkeys():
            self.assertEquals(m1[key], m2[key], 1e-6)

    def getName(self):

        return type(self).__name__

    def _assertSaneFieldCaches(self, msg):

        entries = FieldCache.DEFAULT.getCacheEntries()

        insanity = FieldCacheSanityChecker.checkSanity(entries)
        if insanity:
            print [x for x in insanity]
        self.assertEqual(0, len(insanity),
                         msg + ": Insane FieldCache usage(s) found")


class MyFieldComparator(PythonFieldComparator):

    def __init__(self, numHits):
        super(MyFieldComparator, self).__init__()
        self.slotValues = [0] * numHits

    def copy(self, slot, doc):
        self.slotValues[slot] = self.docValues.get(doc)

    def compare(self, slot1, slot2):
        return self.slotValues[slot1] - self.slotValues[slot2]

    def compareBottom(self, doc):
        return self.bottomValue - self.docValues.get(doc)

    def setBottom(self, bottom):
        self.bottomValue = self.slotValues[bottom]

    def setNextReader(self, context):
        
        class intParser(PythonIntParser):
            def parseInt(_self, val):
                return (val.bytes[val.offset] - ord('A')) * 123456
            def termsEnum(_self, terms):
                return terms.iterator(None)
                
        self.docValues = FieldCache.DEFAULT.getInts(context.reader(), "parser",
                                                    intParser(), False)

        return self

    def value(self, slot):
        return Integer(self.slotValues[slot])

    def compareDocToValue(self, doc, valueObj):
        value = valueObj.intValue()
        docValue = self.docValues.get(doc)

        # values are small enough that overflow won't happen
        return docValue - value


class MyFieldComparatorSource(PythonFieldComparatorSource):

    def newComparator(self, fieldname, numHits, sortPos, reversed):

        # keep an extra ref since this object seems to be passed around
        # back and forth without a reference being kept on the java side
        self.saved = MyFieldComparator(numHits)
        return self.saved


if __name__ == "__main__":
    env = lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    if '-loop' in sys.argv:
        sys.argv.remove('-loop')
        while True:
            try:
                unittest.main()
            except:
                pass
#            refs = sorted(env._dumpRefs(classes=True).items(),
#                          key=lambda x: x[1], reverse=True)
#            print refs[0:4]
    else:
        unittest.main()
