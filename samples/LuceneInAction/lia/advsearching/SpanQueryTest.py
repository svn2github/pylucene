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

from unittest import TestCase
from cStringIO import StringIO

from lucene import \
     WhitespaceAnalyzer, Document, Field, IndexReader, IndexWriter, Term, \
     IndexSearcher, PhraseQuery, SpanFirstQuery, SpanNearQuery, SpanNotQuery, \
     SpanOrQuery, SpanTermQuery, RAMDirectory, Hit

from lia.analysis.AnalyzerUtils import AnalyzerUtils


class SpanQueryTest(TestCase):

    def setUp(self):

        self.directory = RAMDirectory()
        self.analyzer = WhitespaceAnalyzer()

        writer = IndexWriter(self.directory, self.analyzer, True)

        doc = Document()
        doc.add(Field("f", "the quick brown fox jumps over the lazy dog",
                      Field.Store.YES, Field.Index.TOKENIZED))
        writer.addDocument(doc)

        doc = Document()
        doc.add(Field("f", "the quick red fox jumps over the sleepy cat",
                      Field.Store.YES, Field.Index.TOKENIZED))
        writer.addDocument(doc)

        writer.close()

        self.searcher = IndexSearcher(self.directory)
        self.reader = IndexReader.open(self.directory)

        self.quick = SpanTermQuery(Term("f", "quick"))
        self.brown = SpanTermQuery(Term("f", "brown"))
        self.red = SpanTermQuery(Term("f", "red"))
        self.fox = SpanTermQuery(Term("f", "fox"))
        self.lazy = SpanTermQuery(Term("f", "lazy"))
        self.sleepy = SpanTermQuery(Term("f", "sleepy"))
        self.dog = SpanTermQuery(Term("f", "dog"))
        self.cat = SpanTermQuery(Term("f", "cat"))

    def assertOnlyBrownFox(self, query):

        hits = self.searcher.search(query)
        self.assertEqual(1, len(hits))
        self.assertEqual(0, hits.id(0), "wrong doc")

    def assertBothFoxes(self, query):

        hits = self.searcher.search(query)
        self.assertEqual(2, len(hits))

    def assertNoMatches(self, query):

        hits = self.searcher.search(query)
        self.assertEquals(0, len(hits))

    def testSpanTermQuery(self):

        self.assertOnlyBrownFox(self.brown)
        self.dumpSpans(self.brown)

    def testSpanFirstQuery(self):

        sfq = SpanFirstQuery(self.brown, 2)
        self.assertNoMatches(sfq)

        self.dumpSpans(sfq)

        sfq = SpanFirstQuery(self.brown, 3)
        self.dumpSpans(sfq)
        self.assertOnlyBrownFox(sfq)

    def testSpanNearQuery(self):

        quick_brown_dog = [self.quick, self.brown, self.dog]
        snq = SpanNearQuery(quick_brown_dog, 0, True)
        self.assertNoMatches(snq)
        self.dumpSpans(snq)

        snq = SpanNearQuery(quick_brown_dog, 4, True)
        self.assertNoMatches(snq)
        self.dumpSpans(snq)

        snq = SpanNearQuery(quick_brown_dog, 5, True)
        self.assertOnlyBrownFox(snq)
        self.dumpSpans(snq)

        # interesting - even a sloppy phrase query would require
        # more slop to match
        snq = SpanNearQuery([self.lazy, self.fox], 3, False)
        self.assertOnlyBrownFox(snq)
        self.dumpSpans(snq)

        pq = PhraseQuery()
        pq.add(Term("f", "lazy"))
        pq.add(Term("f", "fox"))
        pq.setSlop(4)
        self.assertNoMatches(pq)

        pq.setSlop(5)
        self.assertOnlyBrownFox(pq)

    def testSpanNotQuery(self):

        quick_fox = SpanNearQuery([self.quick, self.fox], 1, True)
        self.assertBothFoxes(quick_fox)
        self.dumpSpans(quick_fox)

        quick_fox_dog = SpanNotQuery(quick_fox, self.dog)
        self.assertBothFoxes(quick_fox_dog)
        self.dumpSpans(quick_fox_dog)

        no_quick_red_fox = SpanNotQuery(quick_fox, self.red)
        self.assertOnlyBrownFox(no_quick_red_fox)
        self.dumpSpans(no_quick_red_fox)

    def testSpanOrQuery(self):

        quick_fox = SpanNearQuery([self.quick, self.fox], 1, True)
        lazy_dog = SpanNearQuery([self.lazy, self.dog], 0, True)
        sleepy_cat = SpanNearQuery([self.sleepy, self.cat], 0, True)
        qf_near_ld = SpanNearQuery([quick_fox, lazy_dog], 3, True)

        self.assertOnlyBrownFox(qf_near_ld)
        self.dumpSpans(qf_near_ld)

        qf_near_sc = SpanNearQuery([quick_fox, sleepy_cat], 3, True)
        self.dumpSpans(qf_near_sc)

        orQ = SpanOrQuery([qf_near_ld, qf_near_sc])
        self.assertBothFoxes(orQ)
        self.dumpSpans(orQ)

    def testPlay(self):

        orQ = SpanOrQuery([self.quick, self.fox])
        self.dumpSpans(orQ)

        quick_fox = SpanNearQuery([self.quick, self.fox], 1, True)
        sfq = SpanFirstQuery(quick_fox, 4)
        self.dumpSpans(sfq)

        self.dumpSpans(SpanTermQuery(Term("f", "the")))

        quick_brown = SpanNearQuery([self.quick, self.brown], 0, False)
        self.dumpSpans(quick_brown)

    def dumpSpans(self, query):

        spans = query.getSpans(self.reader)
        print "%s:" % query
        numSpans = 0

        hits = self.searcher.search(query)
        scores = [0, 0]
        for hit in hits:
            hit = Hit.cast_(hit)
            scores[hit.getId()] = hit.getScore()

        while spans.next():
            numSpans += 1

            id = spans.doc()
            doc = self.reader.document(id)

            # for simplicity - assume tokens are in sequential,
            # positions, starting from 0
            tokens = AnalyzerUtils.tokensFromAnalysis(self.analyzer, doc["f"])
            buffer = StringIO()
            buffer.write("   ")

            i = 0
            for token in tokens:
                if i == spans.start():
                    buffer.write("<")

                buffer.write(token.termText())
                if i + 1 == spans.end():
                    buffer.write(">")

                buffer.write(" ")
                i += 1
      
            buffer.write("(")
            buffer.write(str(scores[id]))
            buffer.write(") ")

            print buffer.getvalue()
            # print self.searcher.explain(query, id)

        if numSpans == 0:
            print "   No spans"

        print ''
