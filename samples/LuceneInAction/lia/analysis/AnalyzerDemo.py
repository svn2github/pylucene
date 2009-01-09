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


from lia.analysis.AnalyzerUtils import AnalyzerUtils
from lucene import \
     StopAnalyzer, SimpleAnalyzer, WhitespaceAnalyzer, StandardAnalyzer


class AnalyzerDemo(object):

    examples = ["The quick brown fox jumped over the lazy dogs",
                "XY&Z Corporation - xyz@example.com"]
    
    analyzers = [WhitespaceAnalyzer(),
                 SimpleAnalyzer(),
                 StopAnalyzer(),
                 StandardAnalyzer()]

    def main(cls, argv):

        # Use the embedded example strings, unless
        # command line arguments are specified, then use those.
        strings = cls.examples

        if len(argv) > 1:
            strings = argv[1:]

        for string in strings:
            cls.analyze(string)

    def analyze(cls, text):

        print'"Analyzing "', text, '"'

        for analyzer in cls.analyzers:
            name = type(analyzer).__name__
            print " %s:" %(name),
            AnalyzerUtils.displayTokens(analyzer, text)
            print ''
        print ''

    main = classmethod(main)
    analyze = classmethod(analyze)


if __name__ == "__main__":
    import sys
    AnalyzerDemo.main(sys.argv)
