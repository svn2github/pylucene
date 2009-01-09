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
from lucene import FSDirectory, Document, System, SimpleDateFormat, Hit


class LiaTestCase(TestCase):

    def __init__(self, *args):

        super(LiaTestCase, self).__init__(*args)
        self.indexDir = System.getProperty("index.dir")

    def setUp(self):

        self.directory = FSDirectory.getDirectory(self.indexDir, False)

    def tearDown(self):

        self.directory.close()

    #
    # For troubleshooting
    #
    def dumpHits(self, hits):

        if not hits:
            print "No hits"
        else:
            for hit in hits:
                hit = Hit.cast_(hit)
                print "%s: %s" %(hit.getScore(),
                                 hit.getDocument().get('title'))

    def assertHitsIncludeTitle(self, hits, title):

        for hit in hits:
            doc = Hit.cast_(hit).getDocument()
            if title == doc.get("title"):
                self.assert_(True)
                return

        self.fail("title '%s' not found" %(title))

    def parseDate(self, s):

        return SimpleDateFormat("yyyy-MM-dd").parse(s)
