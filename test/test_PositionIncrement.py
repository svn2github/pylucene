# ====================================================================
#   Copyright (c) 2004-2008 Open Source Applications Foundation
#
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
from lucene import *


class PositionIncrementTestCase(TestCase):
    """
    Unit tests ported from Java Lucene
    """

    def testSetPosition(self):

        class _analyzer(PythonAnalyzer):
            def tokenStream(self, fieldName, reader):
                class _tokenStream(PythonTokenStream):
                    def __init__(self):
                        super(_tokenStream, self).__init__()
                        self.TOKENS = ["1", "2", "3", "4", "5"]
                        self.INCREMENTS = [1, 2, 1, 0, 1]
                        self.i = 0
                    def next(self):
                        if self.i == len(self.TOKENS):
                            return None
                        t = Token(self.TOKENS[self.i], self.i, self.i)
                        t.setPositionIncrement(self.INCREMENTS[self.i])
                        self.i += 1
                        return t
                    def reset(self):
                        pass
                    def close(self):
                        pass
                return _tokenStream()

        analyzer = _analyzer()

        store = RAMDirectory()
        writer = IndexWriter(store, analyzer, True)
        d = Document()
        d.add(Field("field", "bogus",
                    Field.Store.YES, Field.Index.TOKENIZED))
        writer.addDocument(d)
        writer.optimize()
        writer.close()

        searcher = IndexSearcher(store)

        q = PhraseQuery()
        q.add(Term("field", "1"))
        q.add(Term("field", "2"))
        hits = searcher.search(q)
        self.assertEqual(0, hits.length())

        q = PhraseQuery()
        q.add(Term("field", "2"))
        q.add(Term("field", "3"))
        hits = searcher.search(q)
        self.assertEqual(1, hits.length())

        q = PhraseQuery()
        q.add(Term("field", "3"))
        q.add(Term("field", "4"))
        hits = searcher.search(q)
        self.assertEqual(0, hits.length())

        q = PhraseQuery()
        q.add(Term("field", "2"))
        q.add(Term("field", "4"))
        hits = searcher.search(q)
        self.assertEqual(1, hits.length())

        q = PhraseQuery()
        q.add(Term("field", "3"))
        q.add(Term("field", "5"))
        hits = searcher.search(q)
        self.assertEqual(1, hits.length())

        q = PhraseQuery()
        q.add(Term("field", "4"))
        q.add(Term("field", "5"))
        hits = searcher.search(q)
        self.assertEqual(1, hits.length())

        q = PhraseQuery()
        q.add(Term("field", "2"))
        q.add(Term("field", "5"))
        hits = searcher.search(q)
        self.assertEqual(0, hits.length())

    def testIncrementingPositions(self):
        """
        Basic analyzer behavior should be to keep sequential terms in one
        increment from one another.
        """
        
        analyzer = WhitespaceAnalyzer()
        ts = analyzer.tokenStream("field",
                                  StringReader(u"one two three four five"))

        for token in ts:
            self.assertEqual(1, token.getPositionIncrement(),
                             token.termText())


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
