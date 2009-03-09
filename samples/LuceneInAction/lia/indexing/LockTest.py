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

from lucene import VERSION, \
     IndexWriter, IndexReader, SimpleAnalyzer, FSDirectory, System


class LockTest(TestCase):

    def setUp(self):

        indexDir = os.path.join(System.getProperty("java.io.tmpdir", "tmp"),
                                "index")
        self.dir = FSDirectory.getDirectory(indexDir, True)

    def testWriteLock(self):

        if VERSION < '2.1.0':
            writer1 = None
            writer2 = None
            gotException = False

            try:
                try:
                    writer1 = IndexWriter(self.dir, SimpleAnalyzer(), True)
                    writer2 = IndexWriter(self.dir, SimpleAnalyzer(), True)

                    self.fail("We should never reach this point")
                except:
                    gotException = True
            finally:
                writer1.close()
                self.assert_(writer2 is None)
                self.assert_(gotException)

    def testCommitLock(self):

        reader1 = None
        reader2 = None

        try:
            writer = IndexWriter(self.dir, SimpleAnalyzer(), True)
            writer.close()

            reader1 = IndexReader.open(self.dir)
            reader2 = IndexReader.open(self.dir)
        finally:
            reader1.close()
            reader2.close()
