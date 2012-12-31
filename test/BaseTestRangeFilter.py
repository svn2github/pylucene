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

import lucene  # so as to get 'org'

from random import seed, randint
from PyLuceneTestCase import PyLuceneTestCase

from org.apache.lucene.analysis.core import SimpleAnalyzer
from org.apache.lucene.document import Document, Field, StringField
from org.apache.lucene.store import RAMDirectory
from org.apache.lucene.util import Version


class BaseTestRangeFilter(PyLuceneTestCase):

    def __init__(self, *args):

        super(BaseTestRangeFilter, self).__init__(*args)

        # 
        # Collation interacts badly with hyphens -- collation produces
        # different ordering than Unicode code-point ordering -- so two
        # indexes are created: one which can't have negative random
        # integers, for testing collated ranges, and the other which can
        # have negative random integers, for all other tests.
        #

        self.MAX_INT = 0x7fffffff

        class TestIndex(object):
            def __init__(_self, minR, maxR, allowNegativeRandomInts):
                _self.minR = minR
                _self.maxR = maxR
                _self.allowNegativeRandomInts = allowNegativeRandomInts
                _self.index = RAMDirectory()

        self.signedIndex = TestIndex(self.MAX_INT, ~self.MAX_INT, True)
        self.unsignedIndex = TestIndex(self.MAX_INT, 0, False)

        self.minId = 0
        self.maxId = 10000

        self.build(self.signedIndex)
        self.build(self.unsignedIndex)

    #
    # a simple padding function that should work with any int
    #

    def pad(self, n):

        if n < 0:
            return "-%0.10d" % (self.MAX_INT + n + 1)
        else:
            return "0%0.10d" % n

    def build(self, index):

        writer = self.getWriter(directory=index.index,
                                analyzer=SimpleAnalyzer(Version.LUCENE_CURRENT))

        seed(101)
        for d in xrange(self.minId, self.maxId + 1):
            doc = Document()
            doc.add(Field("id", self.pad(d), StringField.TYPE_STORED))
            if index.allowNegativeRandomInts:
                r = randint(~self.MAX_INT, self.MAX_INT)
            else:
                r = randint(0, self.MAX_INT)

            if index.maxR < r:
                index.maxR = r

            if r < index.minR:
                index.minR = r

            doc.add(Field("rand", self.pad(r), StringField.TYPE_STORED))
            doc.add(Field("body", "body", StringField.TYPE_STORED))
            writer.addDocument(doc)
            
        writer.commit()
        writer.close()

    def testPad(self):

        tests = [-9999999, -99560, -100, -3, -1, 0, 3, 9, 10, 1000, 999999999]

        for i in xrange(0, len(tests) - 1):
            a = tests[i]
            b = tests[i + 1]
            aa = self.pad(a)
            bb = self.pad(b)
            label = "%s:%s vs %s:%s" %(a, aa, b, bb)
            self.assertEqual(len(aa), len(bb), "length of %s" %label)
            self.assert_(aa < bb, "compare less than %s" %label)
