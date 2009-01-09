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

from lia.indexing.BaseIndexingTestCase import BaseIndexingTestCase
from lucene import IndexReader, RAMDirectory


class FS2RAMDirectoryTest(BaseIndexingTestCase):

    def testSlurp(self):

        fsDirReader = IndexReader.open(self.dir)
        self.assertEqual(len(self.keywords), fsDirReader.maxDoc())
        self.assertEqual(len(self.keywords), fsDirReader.numDocs())

        ramDir = RAMDirectory(self.dir)
        ramDirReader = IndexReader.open(ramDir)
        self.assertEqual(fsDirReader.maxDoc(), ramDirReader.maxDoc())
        self.assertEqual(fsDirReader.numDocs(), ramDirReader.numDocs())

        fsDirReader.close()
        ramDir.close()
