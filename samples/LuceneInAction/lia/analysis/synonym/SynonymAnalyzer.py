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

from lucene import \
     LowerCaseFilter, StopFilter, \
     StandardAnalyzer, StandardTokenizer, StandardFilter, PythonAnalyzer

from lia.analysis.synonym.SynonymFilter import SynonymFilter

#
# An Analyzer extension
#

class SynonymAnalyzer(PythonAnalyzer):

    def __init__(self, engine):

        super(SynonymAnalyzer, self).__init__()
        self.engine = engine

    def tokenStream(self, fieldName, reader):

        tokenStream = LowerCaseFilter(StandardFilter(StandardTokenizer(reader)))
        tokenStream = StopFilter(tokenStream, StandardAnalyzer.STOP_WORDS)
        
        return SynonymFilter(tokenStream, self.engine)
