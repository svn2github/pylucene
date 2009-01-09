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

from unittest import TestCase, main
from lucene import *


class TestFormatter(PythonFormatter):

    def __init__(self, testCase):
        super(TestFormatter, self).__init__()
        self.testCase = testCase

    def highlightTerm(self, originalText, group):
        if group.getTotalScore() <= 0:
            return originalText;
        
        self.testCase.countHighlightTerm()
        
        return "<b>" + originalText + "</b>"
    

class HighlighterTestCase(TestCase):
    """
    Unit tests ported from Java Lucene.
    2004 by Yura Smolsky ;)
    """

    FIELD_NAME = "contents"
    texts = [ "A wicked problem is one for which each attempt to create a solution changes the understanding of the problem.  Wicked problems cannot be solved in a traditional linear fashion, because the problem definition evolves as new possible solutions are considered and/or implemented."
              "Wicked problems always occur in a social context -- the wickedness of the problem reflects the diversity among the stakeholders in the problem."
              "From http://cognexus.org/id42.htm"
              "Most projects in organizations -- and virtually all technology-related projects these days -- are about wicked problems.  Indeed, it is the social complexity of these problems, not their technical complexity, that overwhelms most current problem solving and project management approaches."
              "This text has a typo in referring to whicked problems" ];

    def __init__(self, *args):

        super(HighlighterTestCase, self).__init__(*args)
        self.parser = QueryParser(self.FIELD_NAME, StandardAnalyzer())

    def testSimpleHighlighter(self):

        self.doSearching("Wicked")
        highlighter = Highlighter(QueryScorer(self.query))
        highlighter.setTextFragmenter(SimpleFragmenter(40))
        maxNumFragmentsRequired = 2

        for i in range(0, self.hits.length()):
            text = self.hits.doc(i).get(self.FIELD_NAME)
            tokenStream = self.analyzer.tokenStream(self.FIELD_NAME,
                                                    StringReader(text))

            result = highlighter.getBestFragments(tokenStream, text,
                                                  maxNumFragmentsRequired,
                                                  "...")
            print "\t", result

        # Not sure we can assert anything here - just running to check we don't
        # throw any exceptions

    def testGetBestFragmentsSimpleQuery(self):

        self.doSearching("Wicked")
        self.doStandardHighlights()
        self.assert_(self.numHighlights == 3,
                     ("Failed to find correct number of highlights, %d found"
                      %(self.numHighlights)))
        
    def doSearching(self, queryString):

        searcher = IndexSearcher(self.ramDir)
        self.query = self.parser.parse(queryString)
        # for any multi-term queries to work (prefix, wildcard, range,
        # fuzzy etc) you must use a rewritten query!
        self.query = self.query.rewrite(self.reader)

        print "Searching for:", self.query.toString(self.FIELD_NAME)
        self.hits = searcher.search(self.query)
        self.numHighlights = 0

    def doStandardHighlights(self):
        
        formatter = TestFormatter(self)
        
        highlighter = Highlighter(formatter, QueryScorer(self.query))
        highlighter.setTextFragmenter(SimpleFragmenter(20))
        for i in range(0, self.hits.length()):
            text = self.hits.doc(i).get(self.FIELD_NAME)
            maxNumFragmentsRequired = 2
            fragmentSeparator = "..."
            tokenStream = self.analyzer.tokenStream(self.FIELD_NAME,
                                                    StringReader(text))

            result = highlighter.getBestFragments(tokenStream,
                                                  text,
                                                  maxNumFragmentsRequired,
                                                  fragmentSeparator)
            print "\t", result
            
    def countHighlightTerm(self):

        self.numHighlights += 1 # update stats used in assertions
        
    def setUp(self):

        self.analyzer=StandardAnalyzer()
        self.ramDir = RAMDirectory()
        writer = IndexWriter(self.ramDir, self.analyzer, True)
        for text in self.texts:
            self.addDoc(writer, text)

        writer.optimize()
        writer.close()
        self.reader = IndexReader.open(self.ramDir)
        self.numHighlights = 0;

    def addDoc(self, writer, text):

        d = Document()
        f = Field(self.FIELD_NAME, text,
                  Field.Store.YES, Field.Index.TOKENIZED,
                  Field.TermVector.YES)
        d.add(f)
        writer.addDocument(d)
        

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
