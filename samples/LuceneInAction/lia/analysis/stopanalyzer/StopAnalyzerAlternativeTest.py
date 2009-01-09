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

from unittest import TestCase
from lucene import StopAnalyzer

from lia.analysis.AnalyzerUtils import AnalyzerUtils
from lia.analysis.stopanalyzer.StopAnalyzerFlawed import StopAnalyzerFlawed
from lia.analysis.stopanalyzer.StopAnalyzer2 import StopAnalyzer2


class StopAnalyzerAlternativeTest(TestCase):

    def testStopAnalyzer2(self):

        tokens = AnalyzerUtils.tokensFromAnalysis(StopAnalyzer2(),
                                                  "The quick brown...")
        AnalyzerUtils.assertTokensEqual(self, tokens, ["quick", "brown"])

    def testStopAnalyzerFlawed(self):

        tokens = AnalyzerUtils.tokensFromAnalysis(StopAnalyzerFlawed(),
                                                  "The quick brown...")
        self.assertEqual("the", tokens[0].termText())


    #
    # Illustrates that "the" is not removed, although it is lowercased
    #

    def main(cls):

        AnalyzerUtils.displayTokens(StopAnalyzerFlawed(),
                                    "The quick brown...")

    main = classmethod(main)
