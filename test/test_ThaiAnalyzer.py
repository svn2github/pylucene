# -*- coding: utf-8 -*-
# ====================================================================
#   Copyright (c) 2004-2008 Open Source Applications Foundation
#
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

from unittest import TestCase, main
from lucene import ThaiAnalyzer, StringReader


class ThaiAnalyzerTestCase(TestCase):

    def assertAnalyzesTo(self, analyzer, input, output):

        tokenStream = analyzer.tokenStream("dummy", StringReader(input))

        for termText in output:
            token = tokenStream.next()
            self.assert_(token is not None)
            self.assertEqual(token.termText(), termText)

        self.assert_(not list(tokenStream))
        tokenStream.close()

    def testAnalyzer(self):

        analyzer = ThaiAnalyzer()
    
        self.assertAnalyzesTo(analyzer, u"", [])

        self.assertAnalyzesTo(analyzer,
                              u"การที่ได้ต้องแสดงว่างานดี",
                              [ u"การ", u"ที่", u"ได้", u"ต้อง",
                                u"แสดง", u"ว่า", u"งาน", u"ดี" ])

        self.assertAnalyzesTo(analyzer,
                              u"บริษัทชื่อ XY&Z - คุยกับ xyz@demo.com",
                              [ u"บริษัท", u"ชื่อ", u"xy&z", u"คุย", u"กับ", u"xyz@demo.com" ])

        # English stop words
        self.assertAnalyzesTo(analyzer,
                              u"ประโยคว่า The quick brown fox jumped over the lazy dogs",
                              [ u"ประโยค", u"ว่า", u"quick", u"brown", u"fox",
                                u"jumped", u"over", u"lazy", u"dogs" ])


if __name__ == "__main__":
    import sys, lucene
    lucene.initVM(lucene.CLASSPATH)
    if '-loop' in sys.argv:
        sys.argv.remove('-loop')
        while True:
            try:
                main()
            except:
                pass
    else:
        main()
