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

from lia.common.LiaTestCase import LiaTestCase

from lucene import Term, IndexSearcher, RangeQuery


class RangeQueryTest(LiaTestCase):

    def setUp(self):

        super(RangeQueryTest, self).setUp()

        self.begin = Term("pubmonth", "198805")

        # pub date of TTC was October 1988
        self.end = Term("pubmonth", "198810")

    def testInclusive(self):

        query = RangeQuery(self.begin, self.end, True)
        searcher = IndexSearcher(self.directory)

        hits = searcher.search(query)
        self.assertEqual(1, hits.length(), "tao")

    def testExclusive(self):

        query = RangeQuery(self.begin, self.end, False)
        searcher = IndexSearcher(self.directory)

        hits = searcher.search(query)
        self.assertEqual(0, hits.length(), "there is no tao")
