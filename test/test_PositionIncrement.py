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

import sys, lucene, unittest
from lucene import JArray
from PyLuceneTestCase import PyLuceneTestCase
from MultiSpansWrapper import MultiSpansWrapper

from java.io import StringReader
from org.apache.lucene.analysis import Analyzer
from org.apache.lucene.analysis.core import \
    LowerCaseTokenizer, WhitespaceTokenizer
from org.apache.lucene.analysis.tokenattributes import \
    CharTermAttribute, OffsetAttribute, PayloadAttribute, \
    PositionIncrementAttribute
from org.apache.lucene.document import Document, Field, TextField
from org.apache.lucene.index import MultiFields, Term
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import MultiPhraseQuery, PhraseQuery
from org.apache.lucene.search.payloads import PayloadSpanUtil
from org.apache.lucene.search.spans import SpanNearQuery, SpanTermQuery
from org.apache.lucene.util import BytesRef, Version
from org.apache.pylucene.analysis import \
    PythonAnalyzer, PythonFilteringTokenFilter, PythonTokenFilter, \
    PythonTokenizer


class PositionIncrementTestCase(PyLuceneTestCase):
    """
    Unit tests ported from Java Lucene
    """
    def testSetPosition(self):

        class _tokenizer(PythonTokenizer):
            def __init__(_self, reader):
                super(_tokenizer, _self).__init__(reader)

                _self.TOKENS = ["1", "2", "3", "4", "5"]
                _self.INCREMENTS = [1, 2, 1, 0, 1]
                _self.i = 0
                _self.posIncrAtt = _self.addAttribute(PositionIncrementAttribute.class_)
                _self.termAtt = _self.addAttribute(CharTermAttribute.class_)
                _self.offsetAtt = _self.addAttribute(OffsetAttribute.class_)

            def incrementToken(_self):
                if _self.i == len(_self.TOKENS):
                    return False

                _self.clearAttributes()
                _self.termAtt.append(_self.TOKENS[_self.i])
                _self.offsetAtt.setOffset(_self.i, _self.i)
                _self.posIncrAtt.setPositionIncrement(_self.INCREMENTS[_self.i])
                _self.i += 1

                return True

            def end(_self):
                pass
            def reset(_self):
                pass
            def close(_self):
                pass

        class _analyzer(PythonAnalyzer):
            def createComponents(_self, fieldName, reader):
                return Analyzer.TokenStreamComponents(_tokenizer(reader))

        writer = self.getWriter(analyzer=_analyzer())

        d = Document()
        d.add(Field("field", "bogus", TextField.TYPE_STORED))

        writer.addDocument(d)
        writer.commit()
        writer.close()

        searcher = self.getSearcher()
        reader = searcher.getIndexReader()
        pos = MultiFields.getTermPositionsEnum(reader, MultiFields.getLiveDocs(reader), "field", BytesRef("1"))
        pos.nextDoc()
        # first token should be at position 0
        self.assertEqual(0, pos.nextPosition())
    
        pos = MultiFields.getTermPositionsEnum(reader, MultiFields.getLiveDocs(reader), "field", BytesRef("2"))
        pos.nextDoc()
        # second token should be at position 2
        self.assertEqual(2, pos.nextPosition())
    
        q = PhraseQuery()
        q.add(Term("field", "1"))
        q.add(Term("field", "2"))
        hits = searcher.search(q, None, 1000).scoreDocs
        self.assertEqual(0, len(hits))

        # same as previous, just specify positions explicitely.
        q = PhraseQuery() 
        q.add(Term("field", "1"), 0)
        q.add(Term("field", "2"), 1)
        hits = searcher.search(q, None, 1000).scoreDocs
        self.assertEqual(0, len(hits))

        # specifying correct positions should find the phrase.
        q = PhraseQuery()
        q.add(Term("field", "1"), 0)
        q.add(Term("field", "2"), 2)
        hits = searcher.search(q, None, 1000).scoreDocs
        self.assertEqual(1, len(hits))

        q = PhraseQuery()
        q.add(Term("field", "2"))
        q.add(Term("field", "3"))
        hits = searcher.search(q, None, 1000).scoreDocs
        self.assertEqual(1, len(hits))

        q = PhraseQuery()
        q.add(Term("field", "3"))
        q.add(Term("field", "4"))
        hits = searcher.search(q, None, 1000).scoreDocs
        self.assertEqual(0, len(hits))

        # phrase query would find it when correct positions are specified. 
        q = PhraseQuery()
        q.add(Term("field", "3"), 0)
        q.add(Term("field", "4"), 0)
        hits = searcher.search(q, None, 1000).scoreDocs
        self.assertEqual(1, len(hits))

        # phrase query should fail for non existing searched term 
        # even if there exist another searched terms in the same searched
        # position.
        q = PhraseQuery()
        q.add(Term("field", "3"), 0)
        q.add(Term("field", "9"), 0)
        hits = searcher.search(q, None, 1000).scoreDocs
        self.assertEqual(0, len(hits))

        # multi-phrase query should succed for non existing searched term
        # because there exist another searched terms in the same searched
        # position.

        mq = MultiPhraseQuery()
        mq.add([Term("field", "3"), Term("field", "9")], 0)
        hits = searcher.search(mq, None, 1000).scoreDocs
        self.assertEqual(1, len(hits))

        q = PhraseQuery()
        q.add(Term("field", "2"))
        q.add(Term("field", "4"))
        hits = searcher.search(q, None, 1000).scoreDocs
        self.assertEqual(1, len(hits))

        q = PhraseQuery()
        q.add(Term("field", "3"))
        q.add(Term("field", "5"))
        hits = searcher.search(q, None, 1000).scoreDocs
        self.assertEqual(1, len(hits))

        q = PhraseQuery()
        q.add(Term("field", "4"))
        q.add(Term("field", "5"))
        hits = searcher.search(q, None, 1000).scoreDocs
        self.assertEqual(1, len(hits))

        q = PhraseQuery()
        q.add(Term("field", "2"))
        q.add(Term("field", "5"))
        hits = searcher.search(q, None, 1000).scoreDocs
        self.assertEqual(0, len(hits))

    def testPayloadsPos0(self):

        writer = self.getWriter(analyzer=TestPayloadAnalyzer())

        doc = Document()
        doc.add(Field("content", "a a b c d e a f g h i j a b k k",
                      TextField.TYPE_STORED))
        writer.addDocument(doc)
        reader = writer.getReader()
        writer.close()

        tp = MultiFields.getTermPositionsEnum(reader,
                                              MultiFields.getLiveDocs(reader),
                                              "content", BytesRef("a"))

        count = 0
        self.assert_(tp.nextDoc() != tp.NO_MORE_DOCS)
        # "a" occurs 4 times
        self.assertEqual(4, tp.freq())

        expected = 0
        self.assertEqual(expected, tp.nextPosition())
        self.assertEqual(1, tp.nextPosition())
        self.assertEqual(3, tp.nextPosition())
        self.assertEqual(6, tp.nextPosition())

        # only one doc has "a"
        self.assert_(tp.nextDoc() == tp.NO_MORE_DOCS)

        searcher = self.getSearcher(reader=reader)
    
        stq1 = SpanTermQuery(Term("content", "a"))
        stq2 = SpanTermQuery(Term("content", "k"))
        sqs = [stq1, stq2]
        snq = SpanNearQuery(sqs, 30, False)

        count = 0
        sawZero = False
        pspans = MultiSpansWrapper.wrap(searcher.getTopReaderContext(), snq)
        while pspans.next():
            payloads = pspans.getPayload()
            sawZero |= pspans.start() == 0

            it = payloads.iterator()
            while it.hasNext():
                count += 1
                it.next()

        self.assertEqual(5, count)
        self.assert_(sawZero)

        spans = MultiSpansWrapper.wrap(searcher.getTopReaderContext(), snq)
        count = 0
        sawZero = False
        while spans.next():
            count += 1
            sawZero |= spans.start() == 0

        self.assertEqual(4, count)
        self.assert_(sawZero)
		
        sawZero = False
        psu = PayloadSpanUtil(searcher.getTopReaderContext())
        pls = psu.getPayloadsForQuery(snq)
        count = pls.size()
        it = pls.iterator()
        while it.hasNext():
            bytes = JArray('byte').cast_(it.next())
            s = bytes.string_
            sawZero |= s == "pos: 0"

        self.assertEqual(5, count)
        self.assert_(sawZero)


class StopWhitespaceAnalyzer(PythonAnalyzer):

    def __init__(self, enablePositionIncrements):
        super(StopWhitespaceAnalyzer, self).__init__()

        self.enablePositionIncrements = enablePositionIncrements

    def createComponents(self, fieldName, reader):

        class _stopFilter(PythonFilteringTokenFilter):
            def __init__(_self, tokenStream):
                super(_stopFilter, _self).__init__(Version.LUCENE_CURRENT, tokenStream)
                _self.termAtt = _self.addAttribute(CharTermAttribute.class_);
            def accept(_self):
                return _self.termAtt.toString() != "stop"

        source = WhitespaceTokenizer(Version.LUCENE_CURRENT, reader)
        return Analyzer.TokenStreamComponents(source, _stopFilter(source))


class TestPayloadAnalyzer(PythonAnalyzer):

    def createComponents(self, fieldName, reader):
        source = LowerCaseTokenizer(Version.LUCENE_CURRENT, reader)
        return Analyzer.TokenStreamComponents(source, PayloadFilter(source, fieldName))


class PayloadFilter(PythonTokenFilter):

    def __init__(self, input, fieldName):
        super(PayloadFilter, self).__init__(input)
        self.input = input

        self.fieldName = fieldName
        self.pos = 0
        self.i = 0
        self.posIncrAttr = input.addAttribute(PositionIncrementAttribute.class_)
        self.payloadAttr = input.addAttribute(PayloadAttribute.class_)
        self.termAttr = input.addAttribute(CharTermAttribute.class_)

    def incrementToken(self):

        if self.input.incrementToken():
            bytes = JArray('byte')("pos: %d" %(self.pos))
            self.payloadAttr.setPayload(BytesRef(bytes))

            if self.pos == 0 or self.i % 2 == 1:
                posIncr = 1
            else:
                posIncr = 0

            self.posIncrAttr.setPositionIncrement(posIncr)
            self.pos += posIncr
            self.i += 1
            return True

        return False


if __name__ == "__main__":
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    if '-loop' in sys.argv:
        sys.argv.remove('-loop')
        while True:
            try:
                unittest.main()
            except:
                pass
    else:
         unittest.main()
