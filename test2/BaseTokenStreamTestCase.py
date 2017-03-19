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
from lucene import JArray

from java.io import StringReader
from java.lang import Boolean
from org.apache.lucene.analysis.tokenattributes import \
    OffsetAttribute, CharTermAttribute, TypeAttribute, \
    PositionIncrementAttribute
from org.apache.pylucene.util import PythonAttributeImpl

class BaseTokenStreamTestCase(TestCase):
    """
    some helpers to test Analyzers and TokenStreams
    """

    class CheckClearAttributesAttributeImpl(PythonAttributeImpl):

        def __init__(_self):
            super(PythonAttributeImpl, _self).__init__()
            _self.clearCalled = False

        def getAndResetClearCalled(_self):
            try:
                return _self.clearCalled
            finally:
                _self.clearCalled = False

        def clear(_self):
            _self.clearCalled = True

        def equals(_self, other):
            return (
                CheckClearAttributesAttributeImpl.instance_(other) and
                CheckClearAttributesAttributeImpl.cast_(other).clearCalled ==
                _self.clearCalled)

        def hashCode(_self):
            return 76137213 ^ Boolean.valueOf(_self.clearCalled).hashCode()

        def copyTo(_self, target):
            CheckClearAttributesAttributeImpl.cast_(target).clear()


    def _assertTokenStreamContents(self, ts, output,
                                   startOffsets=None, endOffsets=None,
                                   types=None, posIncrements=None,
                                   finalOffset=None):

        #checkClearAtt = ts.addAttribute(PythonAttribute.class_);

        self.assert_(output is not None)
        self.assert_(ts.hasAttribute(CharTermAttribute.class_),
                                     "has no CharTermAttribute")

        termAtt = ts.getAttribute(CharTermAttribute.class_)

        offsetAtt = None
        if (startOffsets is not None or
            endOffsets is not None or
            finalOffset is not None):
            self.assert_(ts.hasAttribute(OffsetAttribute.class_),
                                         "has no OffsetAttribute")
            offsetAtt = ts.getAttribute(OffsetAttribute.class_)

        typeAtt = None
        if types is not None:
            self.assert_(ts.hasAttribute(TypeAttribute.class_),
                         "has no TypeAttribute")
            typeAtt = ts.getAttribute(TypeAttribute.class_)

        posIncrAtt = None
        if posIncrements is not None:
            self.assert_(ts.hasAttribute(PositionIncrementAttribute.class_),
                         "has no PositionIncrementAttribute")
            posIncrAtt = ts.getAttribute(PositionIncrementAttribute.class_)

        ts.reset()
        for i in xrange(len(output)):
            # extra safety to enforce, that the state is not preserved and
            # also assign bogus values
            ts.clearAttributes()
            termAtt.setEmpty().append("bogusTerm")
            if offsetAtt is not None:
                offsetAtt.setOffset(14584724, 24683243)
            if typeAtt is not None:
                typeAtt.setType("bogusType")
            if posIncrAtt is not None:
                posIncrAtt.setPositionIncrement(45987657)

            self.assert_(ts.incrementToken(), "token %d exists" %(i))
            self.assertEqual(output[i], termAtt.toString(), "term %d" %(i))
            if startOffsets is not None:
                self.assertEqual(startOffsets[i], offsetAtt.startOffset(),
                                 "startOffset %d" %(i))
            if endOffsets is not None:
                self.assertEqual(endOffsets[i], offsetAtt.endOffset(),
                                 "endOffset %d" %(i))
            if types is not None:
                self.assertEqual(types[i], typeAtt.type(), "type %d" %(i))
            if posIncrements is not None:
                self.assertEqual(posIncrements[i],
                                 posIncrAtt.getPositionIncrement(),
                                 "posIncrement %d" %(i))

        self.assert_(not ts.incrementToken(), "end of stream")
        ts.end()
        ts.close()

    def _assertAnalyzesTo(self, a, input, output,
                          startOffsets=None, endOffsets=None,
                          posIncrements=None):

        ts = a.tokenStream("dummy", StringReader(input))
        self._assertTokenStreamContents(ts, output, startOffsets, endOffsets,
                                        None, posIncrements)

    def _assertAnalyzesToReuse(self, a, input, output,
                               startOffsets=None, endOffsets=None,
                               types=None, posIncrements=None):

        ts = a.reusableTokenStream("dummy", StringReader(input))
        self._assertTokenStreamContents(ts, output, startOffsets, endOffsets,
                                        types, posIncrements)

    # simple utility method for testing stemmers
    def _checkOneTerm(self, a, input, expected):
        self._assertAnalyzesTo(a, input, JArray('string')(expected))

    def _checkOneTermReuse(self, a, input, expected):
        self._assertAnalyzesToReuse(a, input, JArray('string')(expected))
