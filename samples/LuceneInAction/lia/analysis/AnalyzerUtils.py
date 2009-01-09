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
     SimpleAnalyzer, Token, TokenStream, StandardAnalyzer, StringReader


class AnalyzerUtils(object):

    def main(cls, argv):

        print "SimpleAnalyzer"
        cls.displayTokensWithFullDetails(SimpleAnalyzer(),
                                         "The quick brown fox....")

        print "\n----"
        print "StandardAnalyzer"
        cls.displayTokensWithFullDetails(StandardAnalyzer(),
                                         "I'll e-mail you at xyz@example.com")

    def tokensFromAnalysis(cls, analyzer, text):
        return [token for token in analyzer.tokenStream("contents", StringReader(text))]

    def displayTokens(cls, analyzer, text):

        for token in cls.tokensFromAnalysis(analyzer, text):
            print "[%s]" %(token.termText()),

    def displayTokensWithPositions(cls, analyzer, text):

        position = 0
        for token in cls.tokensFromAnalysis(analyzer, text):
            increment = token.getPositionIncrement()
            if increment > 0:
                position += increment
                print "\n%d:" %(position),

            print "[%s]" %(token.termText()),

    def displayTokensWithFullDetails(cls, analyzer, text):

        position = 0
        for token in cls.tokensFromAnalysis(analyzer, text):
            increment = token.getPositionIncrement()

            if increment > 0:
                position += increment
                print "\n%s:" %(position),

            print "[%s:%d->%d:%s]" %(token.termText(),
                                     token.startOffset(),
                                     token.endOffset(),
                                     token.type()),

    def assertTokensEqual(cls, unittest, tokens, strings):

        unittest.assertEqual(len(strings), len(tokens))

        i = 0
        for token in tokens:
            unittest.assertEqual(strings[i], token.termText(), "index %d" %(i))
            i += 1

    main = classmethod(main)
    tokensFromAnalysis = classmethod(tokensFromAnalysis)
    displayTokens = classmethod(displayTokens)
    displayTokensWithPositions = classmethod(displayTokensWithPositions)
    displayTokensWithFullDetails = classmethod(displayTokensWithFullDetails)
    assertTokensEqual = classmethod(assertTokensEqual)


if __name__ == "__main__":
    import sys
    AnalyzerUtils.main(sys.argv)
