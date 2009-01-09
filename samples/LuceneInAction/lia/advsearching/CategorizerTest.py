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

from math import pi, sqrt, acos
from lia.common.LiaTestCase import LiaTestCase

from lucene import Document, IndexReader 


class CategorizerTest(LiaTestCase):

    def setUp(self):

        super(CategorizerTest, self).setUp()
        self.categoryMap = {}

        self.buildCategoryVectors()
        self.dumpCategoryVectors()

    def testCategorization(self):
        
        self.assertEqual("/technology/computers/programming/methodology",
                         self.getCategory("extreme agile methodology"))
        self.assertEqual("/education/pedagogy",
                         self.getCategory("montessori education philosophy"))

    def dumpCategoryVectors(self):

        for category, vectorMap in self.categoryMap.iteritems():
            print "Category", category
            for term, freq in vectorMap.iteritems():
                print "   ", term, "=", freq

    def buildCategoryVectors(self):

        reader = IndexReader.open(self.directory)

        for id in xrange(reader.maxDoc()):
            doc = reader.document(id)
            category = doc.get("category")
            vectorMap = self.categoryMap.get(category, None)
            if vectorMap is None:
                vectorMap = self.categoryMap[category] = {}

            termFreqVector = reader.getTermFreqVector(id, "subject")
            self.addTermFreqToMap(vectorMap, termFreqVector)

    def addTermFreqToMap(self, vectorMap, termFreqVector):

        terms = termFreqVector.getTerms()
        freqs = termFreqVector.getTermFrequencies()

        i = 0
        for term in terms:
            if term in vectorMap:
                vectorMap[term] += freqs[i]
            else:
                vectorMap[term] = freqs[i]
            i += 1

    def getCategory(self, subject):

        words = subject.split(' ')

        bestAngle = 2 * pi
        bestCategory = None

        for category, vectorMap in self.categoryMap.iteritems():
            angle = self.computeAngle(words, category, vectorMap)
            if angle != 'nan' and angle < bestAngle:
                bestAngle = angle
                bestCategory = category

        return bestCategory

    def computeAngle(self, words, category, vectorMap):

        # assume words are unique and only occur once

        dotProduct = 0
        sumOfSquares = 0

        for word in words:
            categoryWordFreq = 0

            if word in vectorMap:
                categoryWordFreq = vectorMap[word]

            # optimized because we assume frequency in words is 1
            dotProduct += categoryWordFreq
            sumOfSquares += categoryWordFreq ** 2

        if sumOfSquares == 0:
            return 'nan'

        if sumOfSquares == len(words):
            # avoid precision issues for special case
            # sqrt x * sqrt x = x
            denominator = sumOfSquares 
        else:
            denominator = sqrt(sumOfSquares) * sqrt(len(words))

        return acos(dotProduct / denominator)
