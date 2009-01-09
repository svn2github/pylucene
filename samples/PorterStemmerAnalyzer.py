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

# This sample illustrates how to write an Analyzer 'extension' in Python.
# 
#   What is happening behind the scenes ?
#
# The PorterStemmerAnalyzer python class does not in fact extend Analyzer,
# it merely provides an implementation for Analyzer's abstract tokenStream()
# method. When an instance of PorterStemmerAnalyzer is passed to PyLucene,
# with a call to IndexWriter(store, PorterStemmerAnalyzer(), True) for
# example, the PyLucene SWIG-based glue code wraps it into an instance of
# PythonAnalyzer, a proper java extension of Analyzer which implements a
# native tokenStream() method whose job is to call the tokenStream() method
# on the python instance it wraps. The PythonAnalyzer instance is the
# Analyzer extension bridge to PorterStemmerAnalyzer.

import sys, os
from datetime import datetime
from lucene import *
from IndexFiles import IndexFiles


class PorterStemmerAnalyzer(PythonAnalyzer):

    def tokenStream(self, fieldName, reader):

        result = StandardTokenizer(reader)
        result = StandardFilter(result)
        result = LowerCaseFilter(result)
        result = PorterStemFilter(result)
        result = StopFilter(result, StopAnalyzer.ENGLISH_STOP_WORDS)

        return result


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print IndexFiles.__doc__
        sys.exit(1)
    initVM(CLASSPATH)
    print 'lucene', VERSION
    start = datetime.now()
    try:
        IndexFiles(sys.argv[1], "index", PorterStemmerAnalyzer())
        end = datetime.now()
        print end - start
    except Exception, e:
        print "Failed: ", e
