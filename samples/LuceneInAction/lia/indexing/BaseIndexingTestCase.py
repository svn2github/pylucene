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

import os

from unittest import TestCase

from lucene import \
     FSDirectory, System, \
     Document, Field, SimpleAnalyzer, IndexWriter, IndexReader


class BaseIndexingTestCase(TestCase):
    keywords = ["1", "2"]
    unindexed = ["Netherlands", "Italy"]
    unstored = ["Amsterdam has lots of bridges",
                "Venice has lots of canals"]
    text = ["Amsterdam", "Venice"]

    def setUp(self):

        indexDir = os.path.join(System.getProperty('java.io.tmpdir', 'tmp'),
                                'index-dir')
        self.dir = FSDirectory.getDirectory(indexDir, True)
        self.addDocuments(self.dir)

    def addDocuments(self, dir):

        writer = IndexWriter(dir, self.getAnalyzer(), True)
        writer.setUseCompoundFile(self.isCompound())

        for i in xrange(len(self.keywords)):
            doc = Document()
            doc.add(Field("id", self.keywords[i],
                          Field.Store.YES, Field.Index.UN_TOKENIZED))
            doc.add(Field("country", self.unindexed[i],
                          Field.Store.YES, Field.Index.NO))
            doc.add(Field("contents", self.unstored[i],
                          Field.Store.NO, Field.Index.TOKENIZED))
            doc.add(Field("city", self.text[i],
                          Field.Store.YES, Field.Index.TOKENIZED))
            writer.addDocument(doc)

        writer.optimize()
        writer.close()

    def getAnalyzer(self):

        return SimpleAnalyzer()

    def isCompound(self):

        return True

    def testIndexWriter(self):

        writer = IndexWriter(self.dir, self.getAnalyzer(), False)
        self.assertEqual(len(self.keywords), writer.docCount())
        writer.close()

    def testIndexReader(self):

        reader = IndexReader.open(self.dir)
        self.assertEqual(len(self.keywords), reader.maxDoc())
        self.assertEqual(len(self.keywords), reader.numDocs())
        reader.close()
