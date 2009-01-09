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
