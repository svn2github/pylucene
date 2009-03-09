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
from lucene import *


class FuzzyQueryTestCase(TestCase):
    """
    Unit tests ported from Java Lucene
    """

    def _addDoc(self, text, writer):
        doc = Document()
        doc.add(Field("field", text,
                      Field.Store.YES, Field.Index.TOKENIZED))
        writer.addDocument(doc)

    def testDefaultFuzziness(self):

        directory = RAMDirectory()
        writer = IndexWriter(directory, WhitespaceAnalyzer(), True)
        self._addDoc("aaaaa", writer)
        self._addDoc("aaaab", writer)
        self._addDoc("aaabb", writer)
        self._addDoc("aabbb", writer)
        self._addDoc("abbbb", writer)
        self._addDoc("bbbbb", writer)
        self._addDoc("ddddd", writer)
        writer.optimize()
        writer.close()

        searcher = IndexSearcher(directory)

        query = FuzzyQuery(Term("field", "aaaaa"))
        hits = searcher.search(query)
        self.assertEqual(3, hits.length())

        # not similar enough:
        query = FuzzyQuery(Term("field", "xxxxx"))
        hits = searcher.search(query)
        self.assertEqual(0, hits.length())
        # edit distance to "aaaaa" = 3
        query = FuzzyQuery(Term("field", "aaccc"))
        hits = searcher.search(query)
        self.assertEqual(0, hits.length())

        # query identical to a word in the index:
        query = FuzzyQuery(Term("field", "aaaaa"))
        hits = searcher.search(query)
        self.assertEqual(3, hits.length())
        self.assertEqual(hits.doc(0).get("field"), "aaaaa")
        # default allows for up to two edits:
        self.assertEqual(hits.doc(1).get("field"), "aaaab")
        self.assertEqual(hits.doc(2).get("field"), "aaabb")

        # query similar to a word in the index:
        query = FuzzyQuery(Term("field", "aaaac"))
        hits = searcher.search(query)
        self.assertEqual(3, hits.length())
        self.assertEqual(hits.doc(0).get("field"), "aaaaa")
        self.assertEqual(hits.doc(1).get("field"), "aaaab")
        self.assertEqual(hits.doc(2).get("field"), "aaabb")

        query = FuzzyQuery(Term("field", "ddddX"))
        hits = searcher.search(query)
        self.assertEqual(1, hits.length())
        self.assertEqual(hits.doc(0).get("field"), "ddddd")

        # different field = no match:
        query = FuzzyQuery(Term("anotherfield", "ddddX"))
        hits = searcher.search(query)
        self.assertEqual(0, hits.length())

        searcher.close()
        directory.close()

    def testDefaultFuzzinessLong(self):

        directory = RAMDirectory()
        writer = IndexWriter(directory, WhitespaceAnalyzer(), True)
        self._addDoc("aaaaaaa", writer)
        self._addDoc("segment", writer)
        writer.optimize()
        writer.close()
        searcher = IndexSearcher(directory)

        # not similar enough:
        query = FuzzyQuery(Term("field", "xxxxx"))
        hits = searcher.search(query)
        self.assertEqual(0, hits.length())
        # edit distance to "aaaaaaa" = 3, this matches because
        # the string is longer than
        # in testDefaultFuzziness so a bigger difference is allowed:
        query = FuzzyQuery(Term("field", "aaaaccc"))
        hits = searcher.search(query)
        self.assertEqual(1, hits.length())
        self.assertEqual(hits.doc(0).get("field"), "aaaaaaa")

        # no match, more than half of the characters is wrong:
        query = FuzzyQuery(Term("field", "aaacccc"))
        hits = searcher.search(query)
        self.assertEqual(0, hits.length())

        # "student" and "stellent" are indeed similar to "segment" by default:
        query = FuzzyQuery(Term("field", "student"))
        hits = searcher.search(query)
        self.assertEqual(1, hits.length())
        query = FuzzyQuery(Term("field", "stellent"))
        hits = searcher.search(query)
        self.assertEqual(1, hits.length())

        searcher.close()
        directory.close()


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
