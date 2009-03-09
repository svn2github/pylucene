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
