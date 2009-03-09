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
