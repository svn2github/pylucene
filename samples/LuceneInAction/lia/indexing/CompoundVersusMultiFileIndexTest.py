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
