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
from time import time
from datetime import timedelta

from lucene import \
     IndexWriter, SimpleAnalyzer, Document, Field, System, \
     FSDirectory, RAMDirectory


class FSversusRAMDirectoryTest(TestCase):

    def __init__(self, *args):

        super(FSversusRAMDirectoryTest, self).__init__(*args)
        self.docs = self.loadDocuments(3000, 5)

    def setUp(self):

        fsIndexDir = os.path.join(System.getProperty("java.io.tmpdir", "tmp"),
                                  "fs-index")
        self.ramDir = RAMDirectory()
        self.fsDir = FSDirectory.getDirectory(fsIndexDir, True)

    def testTiming(self):

        ramTiming = self.timeIndexWriter(self.ramDir)
        fsTiming = self.timeIndexWriter(self.fsDir)

        #self.assert_(fsTiming > ramTiming)

        print "RAMDirectory Time:", ramTiming
        print "FSDirectory Time :", fsTiming

    def timeIndexWriter(self, dir):

        start = time()
        self.addDocuments(dir)

        return timedelta(seconds=time() - start)

    def addDocuments(self, dir):

        writer = IndexWriter(dir, SimpleAnalyzer(), True)

        #
        # change to adjust performance of indexing with FSDirectory
        # writer.mergeFactor = writer.mergeFactor
        # writer.maxMergeDocs = writer.maxMergeDocs
        # writer.minMergeDocs = writer.minMergeDocs
        #

        for word in self.docs:
            doc = Document()
            doc.add(Field("keyword", word,
                          Field.Store.YES, Field.Index.UN_TOKENIZED))
            doc.add(Field("unindexed", word,
                          Field.Store.YES, Field.Index.NO))
            doc.add(Field("unstored", word,
                          Field.Store.NO, Field.Index.TOKENIZED))
            doc.add(Field("text", word,
                          Field.Store.YES, Field.Index.TOKENIZED))
            writer.addDocument(doc)

        writer.optimize()
        writer.close()

    def loadDocuments(self, numDocs, wordsPerDoc):

        return ["Bibamus " * wordsPerDoc] * numDocs
