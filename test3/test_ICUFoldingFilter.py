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
#  Port of java/org/apache/lucene/analysis/icu/ICUFoldingFilter.java
#  using IBM's C++ ICU wrapped by PyICU (http://pyicu.osafoundation.org)

try:
    from icu import Normalizer2, UNormalizationMode2
except ImportError as e:
    pass

import sys, lucene, unittest
from BaseTokenStreamTestCase import BaseTokenStreamTestCase

from org.apache.lucene.analysis import Analyzer
from org.apache.lucene.analysis.core import WhitespaceTokenizer
from org.apache.pylucene.analysis import PythonAnalyzer


class TestICUFoldingFilter(BaseTokenStreamTestCase):

    def testDefaults(self):

        from lucene.ICUFoldingFilter import ICUFoldingFilter

        class _analyzer(PythonAnalyzer):
            def createComponents(_self, fieldName):
                source = WhitespaceTokenizer()
                return Analyzer.TokenStreamComponents(source, ICUFoldingFilter(source))
            def initReader(_self, fieldName, reader):
                return reader

        a = _analyzer()

        # case folding
        self._assertAnalyzesTo(a, "This is a test",
                               [ "this", "is", "a", "test" ])

        # case folding
        self._assertAnalyzesTo(a, "Ruß", [ "russ" ])

        # case folding with accent removal
        self._assertAnalyzesTo(a, "ΜΆΪΟΣ", [ "μαιοσ" ])
        self._assertAnalyzesTo(a, "Μάϊος", [ "μαιοσ" ])

        # supplementary case folding
        self._assertAnalyzesTo(a, "𐐖", [ "𐐾" ])

        # normalization
        self._assertAnalyzesTo(a, "ﴳﴺﰧ", [ "طمطمطم" ])

        # removal of default ignorables
        self._assertAnalyzesTo(a, "क्‍ष", [ "कष" ])

        # removal of latin accents (composed)
        self._assertAnalyzesTo(a, "résumé", [ "resume" ])

        # removal of latin accents (decomposed)
        self._assertAnalyzesTo(a, "re\u0301sume\u0301", [ "resume" ])

        # fold native digits
        self._assertAnalyzesTo(a, "৭০৬", [ "706" ])

        # ascii-folding-filter type stuff
        self._assertAnalyzesTo(a, "đis is cræzy", [ "dis", "is", "craezy" ])


if __name__ == "__main__":
    try:
        import icu
    except ImportError:
        pass
    else:
        if icu.ICU_VERSION >= '49' and icu.ICU_VERSION <= '59.1':
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
        else:
            print("ICU version [49 - 59.1] is required, running:", icu.ICU_VERSION, file=sys.stderr)
