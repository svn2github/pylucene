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

from lucene import IndexWriter, IndexReader
from lia.indexing.BaseIndexingTestCase import BaseIndexingTestCase


class DocumentDeleteTest(BaseIndexingTestCase):

    def testDeleteBeforeIndexMerge(self):

        reader = IndexReader.open(self.dir)
        self.assertEqual(2, reader.maxDoc())
        self.assertEqual(2, reader.numDocs())
        reader.deleteDocument(1)

        self.assert_(reader.isDeleted(1))
        self.assert_(reader.hasDeletions())
        self.assertEqual(2, reader.maxDoc())
        self.assertEqual(1, reader.numDocs())

        reader.close()

        reader = IndexReader.open(self.dir)

        self.assertEqual(2, reader.maxDoc())
        self.assertEqual(1, reader.numDocs())

        reader.close()

    def testDeleteAfterIndexMerge(self):

        reader = IndexReader.open(self.dir)
        self.assertEqual(2, reader.maxDoc())
        self.assertEqual(2, reader.numDocs())
        reader.deleteDocument(1)
        reader.close()

        writer = IndexWriter(self.dir, self.getAnalyzer(), False)
        writer.optimize()
        writer.close()

        reader = IndexReader.open(self.dir)

        self.assert_(not reader.isDeleted(1))
        self.assert_(not reader.hasDeletions())
        self.assertEqual(1, reader.maxDoc())
        self.assertEqual(1, reader.numDocs())

        reader.close()
