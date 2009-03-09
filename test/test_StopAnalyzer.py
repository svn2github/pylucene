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

from unittest import TestCase, main
from lucene import *


class StopAnalyzerTestCase(TestCase):
    """
    Unit tests ported from Java Lucene
    """

    def setUp(self):

        self.stop = StopAnalyzer()
        self.inValidTokens = StopAnalyzer.ENGLISH_STOP_WORDS[:]

    def testDefaults(self):

        self.assert_(self.stop is not None)
        reader = StringReader("This is a test of the english stop analyzer")
        stream = self.stop.tokenStream("test", reader)
        self.assert_(stream is not None)

        try:
            for token in stream:
                self.assert_(token.termText() not in self.inValidTokens)
        except Exception, e:
            self.fail(str(e))

    def testStopList(self):

        stopWordsSet = []
        stopWordsSet.append("good")
        stopWordsSet.append("test")
        stopWordsSet.append("analyzer")

        newStop = StopAnalyzer(stopWordsSet)
        reader = StringReader("This is a good test of the english stop analyzer")
        stream = newStop.tokenStream("test", reader)
        self.assert_(stream is not None)

        try:
            for token in stream:
                text = token.termText()
                self.assert_(text not in stopWordsSet)
        except Exception, e:
            self.fail(str(e))


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
