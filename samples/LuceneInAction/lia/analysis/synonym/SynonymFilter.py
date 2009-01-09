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

from lucene import Token, PythonTokenFilter

#
# A TokenFilter extension
#

class SynonymFilter(PythonTokenFilter):

    TOKEN_TYPE_SYNONYM = "SYNONYM"
    
    def __init__(self, tokenStream, engine):

        super(SynonymFilter, self).__init__(tokenStream)

        self.synonymStack = []
        self.input = tokenStream
        self.engine = engine

    def next(self):

        if len(self.synonymStack) > 0:
            return self.synonymStack.pop()

        # this raises StopIteration which is cleared to return null to java
        token = self.input.next()
        self.addAliasesToStack(token)

        return token

    def addAliasesToStack(self, token):

        synonyms = self.engine.getSynonyms(token.termText())

        if synonyms is None:
            return

        for synonym in synonyms:
            synToken = Token(synonym, token.startOffset(), token.endOffset(),
                             self.TOKEN_TYPE_SYNONYM)
            synToken.setPositionIncrement(0)
            self.synonymStack.append(synToken)
