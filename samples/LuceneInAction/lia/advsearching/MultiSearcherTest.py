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

from unittest import TestCase
from lucene import \
     WhitespaceAnalyzer, Document, Field, IndexWriter, Term, MultiSearcher, \
     RangeQuery, RAMDirectory, IndexSearcher


class MultiSearcherTest(TestCase):

    def setUp(self):
        
        animals = [ "aardvark", "beaver", "coati",
                    "dog", "elephant", "frog", "gila monster",
                    "horse", "iguana", "javelina", "kangaroo",
                    "lemur", "moose", "nematode", "orca",
                    "python", "quokka", "rat", "scorpion",
                    "tarantula", "uromastyx", "vicuna",
                    "walrus", "xiphias", "yak", "zebra" ]

        analyzer = WhitespaceAnalyzer()

        aTOmDirectory = RAMDirectory()
        nTOzDirectory = RAMDirectory()

        aTOmWriter = IndexWriter(aTOmDirectory, analyzer, True)
        nTOzWriter = IndexWriter(nTOzDirectory, analyzer, True)

        for animal in animals:
            doc = Document()
            doc.add(Field("animal", animal,
                          Field.Store.YES, Field.Index.UN_TOKENIZED))

            if animal[0].lower() < "n":
                aTOmWriter.addDocument(doc)
            else:
                nTOzWriter.addDocument(doc)

        aTOmWriter.close()
        nTOzWriter.close()

        self.searchers = [ IndexSearcher(aTOmDirectory),
                           IndexSearcher(nTOzDirectory) ]

    def testMulti(self):

        searcher = MultiSearcher(self.searchers)

        # range spans documents across both indexes
        query = RangeQuery(Term("animal", "h"), Term("animal", "t"), True)

        hits = searcher.search(query)
        self.assertEqual(12, hits.length(), "tarantula not included")
