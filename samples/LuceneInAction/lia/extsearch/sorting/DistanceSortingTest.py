# ====================================================================
# Copyright (c) 2004-2007 Open Source Applications Foundation.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions: 
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software. 
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
# ====================================================================
#

from math import sqrt
from unittest import TestCase

from lucene import \
     WhitespaceAnalyzer, IndexSearcher, Term, TermQuery, RAMDirectory, \
     Document, Field, IndexWriter, Sort, SortField, FieldDoc, Double

from lia.extsearch.sorting.DistanceComparatorSource import \
     DistanceComparatorSource


class DistanceSortingTest(TestCase):

    def setUp(self):

        self.directory = RAMDirectory()
        writer = IndexWriter(self.directory, WhitespaceAnalyzer(), True)

        self.addPoint(writer, "El Charro", "restaurant", 1, 2)
        self.addPoint(writer, "Cafe Poca Cosa", "restaurant", 5, 9)
        self.addPoint(writer, "Los Betos", "restaurant", 9, 6)
        self.addPoint(writer, "Nico's Taco Shop", "restaurant", 3, 8)

        writer.close()

        self.searcher = IndexSearcher(self.directory)
        self.query = TermQuery(Term("type", "restaurant"))

    def addPoint(self, writer, name, type, x, y):

        doc = Document()
        doc.add(Field("name", name, Field.Store.YES, Field.Index.UN_TOKENIZED))
        doc.add(Field("type", type, Field.Store.YES, Field.Index.UN_TOKENIZED))
        doc.add(Field("location", "%d,%d" %(x, y),
                      Field.Store.YES, Field.Index.UN_TOKENIZED))
        writer.addDocument(doc)

    def testNearestRestaurantToHome(self):

        sort = Sort(SortField("location", DistanceComparatorSource(0, 0)))

        hits = self.searcher.search(self.query, sort)
        self.assertEqual("El Charro", hits.doc(0).get("name"), "closest")
        self.assertEqual("Los Betos", hits.doc(3).get("name"), "furthest")

    def testNeareastRestaurantToWork(self):

        sort = Sort(SortField("location", DistanceComparatorSource(10, 10)))

        docs = self.searcher.search(self.query, None, 3, sort)
        self.assertEqual(4, docs.totalHits)
        self.assertEqual(3, len(docs.scoreDocs))

        fieldDoc = FieldDoc.cast_(docs.scoreDocs[0])
        distance = Double.cast_(fieldDoc.fields[0]).doubleValue()
        self.assertEqual(sqrt(17), distance,
                     "(10,10) -> (9,6) = sqrt(17)")

        document = self.searcher.doc(fieldDoc.doc)
        self.assertEqual("Los Betos", document["name"])

        self.dumpDocs(sort, docs)

    def dumpDocs(self, sort, docs):

        print "Sorted by:", sort

        for scoreDoc in docs.scoreDocs:
            fieldDoc = FieldDoc.cast_(scoreDoc)
            distance = Double.cast_(fieldDoc.fields[0]).doubleValue()
            doc = self.searcher.doc(fieldDoc.doc)
            print "  %(name)s @ (%(location)s) ->" %doc, distance
