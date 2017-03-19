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
#
#  Port of java/org/apache/lucene/analysis/icu/ICUTransformFilter.java
#  using IBM's C++ ICU wrapped by PyICU (http://pyicu.osafoundation.org)

try:
    from icu import Transliterator, UTransDirection
except ImportError as e:
    pass

import sys, lucene, unittest
from BaseTokenStreamTestCase import BaseTokenStreamTestCase

from java.io import StringReader
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.core import KeywordTokenizer
from org.apache.pylucene.analysis import PythonTokenFilter


class TestICUTransformFilter(BaseTokenStreamTestCase):

    def _checkToken(self, transform, input, expected):

        from lucene.ICUTransformFilter import ICUTransformFilter
        tokenizer = KeywordTokenizer()
        tokenizer.setReader(StringReader(input))
        ts = ICUTransformFilter(tokenizer, transform)
        self._assertTokenStreamContents(ts, [ expected ])

    def _getTransliterator(self, name):

        return Transliterator.createInstance(name, UTransDirection.FORWARD)

    def testBasicFunctionality(self):

        self._checkToken(self._getTransliterator("Traditional-Simplified"),
                         "簡化字", "简化字")
        self._checkToken(self._getTransliterator("Katakana-Hiragana"),
                         "ヒラガナ", "ひらがな")
        self._checkToken(self._getTransliterator("Fullwidth-Halfwidth"),
                         "アルアノリウ", "ｱﾙｱﾉﾘｳ")
        self._checkToken(self._getTransliterator("Any-Latin"),
                         "Αλφαβητικός Κατάλογος", "Alphabētikós Katálogos")
        self._checkToken(self._getTransliterator("NFD; [:Nonspacing Mark:] Remove"),
                         "Alphabētikós Katálogos", "Alphabetikos Katalogos")
        self._checkToken(self._getTransliterator("Han-Latin"),
                         "中国", "zhōng guó")

    def testCustomFunctionality(self):

        # convert a's to b's and b's to c's
        rules = "a > b; b > c;"
        self._checkToken(Transliterator.createFromRules("test", rules, UTransDirection.FORWARD), "abacadaba", "bcbcbdbcb")

    def testCustomFunctionality2(self):

        # convert a's to b's and b's to c's
        rules = "c { a > b; a > d;"
        self._checkToken(Transliterator.createFromRules("test", rules, UTransDirection.FORWARD), "caa", "cbd")

    def testOptimizer2(self):

        self._checkToken(self._getTransliterator("Traditional-Simplified; Lower"),
                         "ABCDE", "abcde")


if __name__ == "__main__":
    try:
        import icu
    except ImportError:
        pass
    else:
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
