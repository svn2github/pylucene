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
