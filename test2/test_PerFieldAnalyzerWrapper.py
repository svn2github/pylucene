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
from PyLuceneTestCase import PyLuceneTestCase

from java.io import StringReader
from java.util import HashMap
from org.apache.lucene.analysis.core import SimpleAnalyzer, WhitespaceAnalyzer
from org.apache.lucene.analysis.miscellaneous import PerFieldAnalyzerWrapper
from org.apache.lucene.analysis.tokenattributes import CharTermAttribute


class PerFieldAnalyzerTestCase(PyLuceneTestCase):
    """
    Unit tests ported from Java Lucene
    """

    def testPerField(self):

        perField = HashMap()
        perField.put("special", SimpleAnalyzer())
        analyzer = PerFieldAnalyzerWrapper(WhitespaceAnalyzer(), perField)

        text = "Qwerty"
        tokenStream = analyzer.tokenStream("field", StringReader(text))
        tokenStream.reset()
        termAtt = tokenStream.getAttribute(CharTermAttribute.class_)

        self.assert_(tokenStream.incrementToken())
        self.assertEqual("Qwerty", termAtt.toString(),
                         "WhitespaceAnalyzer does not lowercase")

        tokenStream = analyzer.tokenStream("special", StringReader(text))
        tokenStream.reset()
        termAtt = tokenStream.getAttribute(CharTermAttribute.class_)
        self.assert_(tokenStream.incrementToken())
        self.assertEqual("qwerty", termAtt.toString(),
                         "SimpleAnalyzer lowercases")


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
