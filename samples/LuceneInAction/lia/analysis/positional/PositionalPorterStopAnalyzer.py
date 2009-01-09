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

import sys

from lucene import \
     LowerCaseTokenizer, PorterStemFilter, StopAnalyzer, StopFilter, \
     TokenStream, PythonAnalyzer

from lia.analysis.positional.PositionalStopFilter import PositionalStopFilter

python_ver = '%d.%d.%d' %(sys.version_info[0:3])
if python_ver < '2.4':
    from sets import Set as set


#
# An Analyzer extension
#

class PositionalPorterStopAnalyzer(PythonAnalyzer):

    def __init__(self, stopWords=None):

        super(PositionalPorterStopAnalyzer, self).__init__()

        if stopWords is None:
            stopWords = StopAnalyzer.ENGLISH_STOP_WORDS

        self.stopWords = set(stopWords)

    def tokenStream(self, fieldName, reader):

        tokenStream = LowerCaseTokenizer(reader)
        stopFilter = PositionalStopFilter(tokenStream, self.stopWords)

        return PorterStemFilter(stopFilter)
