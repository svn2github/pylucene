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

import sys, lucene, unittest
from PyLuceneTestCase import PyLuceneTestCase

from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.document import Document
from org.apache.lucene.index import DirectoryReader, IndexWriterConfig
from org.apache.pylucene.index import PythonIndexDeletionPolicy


class MyDeletionPolicy(PythonIndexDeletionPolicy):

    onInitCalled = False
    onCommitCalled = False

    def onInit(self, commits):
      self.onInitCalled = True

    def onCommit(self, commits):
      self.onCommitCalled = True


class IndexDeletionPolicyTestCase(PyLuceneTestCase):

    def getConfig(self, analyzer):

        self.policy = MyDeletionPolicy()
        config = IndexWriterConfig(analyzer)
        config.setIndexDeletionPolicy(self.policy)

        return config

    def testIndexDeletionPolicy(self):

        writer = self.getWriter()

        # no commits exist in the index yet
        self.assertTrue(self.policy.onInitCalled)
        # we haven't called commit yet
        self.assertFalse(self.policy.onCommitCalled)

        doc = Document()
        writer.addDocument(doc)
        writer.commit()

        # now we called commit
        self.assertTrue(self.policy.onCommitCalled)

        # external IR sees 1 commit:
        self.assertEquals(1, DirectoryReader.listCommits(self.directory).size())

        # commit again:
        writer.addDocument(doc)
        writer.commit()

        # external IR sees 2 commits:
        self.assertEquals(2, DirectoryReader.listCommits(self.directory).size())

        writer.close()

        # open same index, make sure both commits survived:
        writer = self.getWriter()

        self.assertTrue(self.policy.onInitCalled)
        self.assertFalse(self.policy.onCommitCalled)
        self.assertEquals(2, DirectoryReader.listCommits(self.directory).size())
        writer.close()

        # 3 from closing writer again
        self.assertEquals(3, DirectoryReader.listCommits(self.directory).size())

if __name__ == "__main__":
    lucene.initVM()
    if '-loop' in sys.argv:
        sys.argv.remove('-loop')
        while True:
            try:
                unittest.main()
            except:
                pass
    else:
         unittest.main()
