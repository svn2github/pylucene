# -*- coding: utf-8 -*-
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
from BaseTokenStreamTestCase import BaseTokenStreamTestCase

from org.apache.lucene.analysis.th import ThaiAnalyzer
from org.apache.lucene.analysis.core import StopAnalyzer
from org.apache.lucene.analysis import CharArraySet


class ThaiAnalyzerTestCase(BaseTokenStreamTestCase):

    def testOffsets(self):
        self._assertAnalyzesTo(ThaiAnalyzer(CharArraySet.EMPTY_SET),
                               u"การที่ได้ต้องแสดงว่างานดี",
                               [ u"การ", u"ที่", u"ได้", u"ต้อง", u"แสดง",
                                 u"ว่า", u"งาน", u"ดี" ],
                               [ 0, 3, 6, 9, 13, 17, 20, 23 ],
                               [ 3, 6, 9, 13, 17, 20, 23, 25 ])


    def testStopWords(self):
        analyzer = ThaiAnalyzer()
        self._assertAnalyzesTo(analyzer, u"การที่ได้ต้องแสดงว่างานดี",
                               [ u"แสดง", u"งาน", u"ดี" ],
                               [ 13, 20, 23 ],
                               [ 17, 23, 25 ],
                               [ 5, 2, 1 ])
        analyzer.close()

    def testPositionIncrements(self):
        analyzer = ThaiAnalyzer(StopAnalyzer.ENGLISH_STOP_WORDS_SET)
        self._assertAnalyzesTo(
            analyzer, u"การที่ได้ต้อง the แสดงว่างานดี",
            [ u"การ", u"ที่", u"ได้", u"ต้อง", u"แสดง", u"ว่า", u"งาน", u"ดี" ],
            [ 0, 3, 6, 9, 18, 22, 25, 28 ],
            [ 3, 6, 9, 13, 22, 25, 28, 30 ],
            [ 1, 1, 1, 1, 2, 1, 1, 1 ])

        # case that a stopword is adjacent to thai text, with no whitespace
        self._assertAnalyzesTo(
            analyzer, u"การที่ได้ต้องthe แสดงว่างานดี",
            [ u"การ", u"ที่", u"ได้", u"ต้อง", u"แสดง", u"ว่า", u"งาน", u"ดี" ],
            [ 0, 3, 6, 9, 17, 21, 24, 27 ],
            [ 3, 6, 9, 13, 21, 24, 27, 29 ],
            [ 1, 1, 1, 1, 2, 1, 1, 1 ])
        analyzer.close()


if __name__ == "__main__":
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    if '-loop' in sys.argv:
        sys.argv.remove('-loop')
        while True:
            try:
                unittest.main()
            except:
                pass
    else:
        unittest.main()
