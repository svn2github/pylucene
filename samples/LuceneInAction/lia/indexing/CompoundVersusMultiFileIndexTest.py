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
     IndexWriter, SimpleAnalyzer, FSDirectory, System, Document, Field


class CompoundVersusMultiFileIndexTest(TestCase):

    def __init__(self, *args):

        super(CompoundVersusMultiFileIndexTest, self).__init__(*args)
        self.docs = self.loadDocuments(5000, 10)

    def setUp(self):

        indexDir = os.path.join(System.getProperty("java.io.tmpdir", "tmp"),
                                "index-dir")

        cIndexDir = "%s-compound" %(indexDir)
        mIndexDir = "%s-multi" %(indexDir)
        self.rmdir(cIndexDir)
        self.rmdir(mIndexDir)

        self.cDir = FSDirectory.getDirectory(cIndexDir, True)
        self.mDir = FSDirectory.getDirectory(mIndexDir, True)

    def rmdir(self, dir):

        for dir, dirnames, filenames in os.walk(dir):
            for filename in filenames:
                os.remove(os.path.join(dir, filename))
            for dirname in dirnames:
                os.rmdir(os.path.join(dir, dirname))

    def testTiming(self):

        cTiming = self.timeIndexWriter(self.cDir, True)
        mTiming = self.timeIndexWriter(self.mDir, False)

        print "Compound Time :", cTiming
        print "Multi-file Time:", mTiming

        self.assert_(cTiming > mTiming)

    def timeIndexWriter(self, dir, isCompound):

        start = time()
        self.addDocuments(dir, isCompound)

        return timedelta(seconds=time() - start)

    def addDocuments(self, dir, isCompound):

        writer = IndexWriter(dir, SimpleAnalyzer(), True)
        writer.setUseCompoundFile(isCompound)

        # change to adjust performance of indexing with FSDirectory
        # writer.mergeFactor = writer.mergeFactor
        # writer.maxMergeDocs = writer.maxMergeDocs
        # writer.minMergeDocs = writer.minMergeDocs

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
