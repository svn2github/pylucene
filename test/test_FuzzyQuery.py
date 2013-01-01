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
from itertools import izip
from lucene import JavaError
from PyLuceneTestCase import PyLuceneTestCase

from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, TextField
from org.apache.lucene.index import MultiReader, Term
from org.apache.lucene.search import FuzzyQuery, MultiTermQuery
from org.apache.lucene.store import RAMDirectory
from org.apache.lucene.util import Version


class FuzzyQueryTestCase(PyLuceneTestCase):
    """
    Unit tests ported from Java Lucene
    """

    def _addDoc(self, text, writer):

        doc = Document()
        doc.add(Field("field", text, TextField.TYPE_STORED))
        writer.addDocument(doc)

    def testDefaultFuzziness(self):

        writer = self.getWriter()

        self._addDoc("aaaaa", writer)
        self._addDoc("aaaab", writer)
        self._addDoc("aaabb", writer)
        self._addDoc("aabbb", writer)
        self._addDoc("abbbb", writer)
        self._addDoc("bbbbb", writer)
        self._addDoc("ddddd", writer)
        writer.commit()
        writer.close()

        searcher = self.getSearcher()

        query = FuzzyQuery(Term("field", "aaaaa"), FuzzyQuery.defaultMaxEdits, 0)
        hits = searcher.search(query, None, 1000).scoreDocs
        self.assertEqual(3, len(hits))

        # same with prefix
        query = FuzzyQuery(Term("field", "aaaaa"), FuzzyQuery.defaultMaxEdits, 1)
        hits = searcher.search(query, None, 1000).scoreDocs
        self.assertEqual(3, len(hits))

        query = FuzzyQuery(Term("field", "aaaaa"), FuzzyQuery.defaultMaxEdits, 2)
        hits = searcher.search(query, None, 1000).scoreDocs
        self.assertEqual(3, len(hits))

        query = FuzzyQuery(Term("field", "aaaaa"), FuzzyQuery.defaultMaxEdits, 3)
        hits = searcher.search(query, None, 1000).scoreDocs
        self.assertEqual(3, len(hits))

        query = FuzzyQuery(Term("field", "aaaaa"), FuzzyQuery.defaultMaxEdits, 4)
        hits = searcher.search(query, None, 1000).scoreDocs
        self.assertEqual(2, len(hits))

        query = FuzzyQuery(Term("field", "aaaaa"), FuzzyQuery.defaultMaxEdits, 5)
        hits = searcher.search(query, None, 1000).scoreDocs
        self.assertEqual(1, len(hits))

        query = FuzzyQuery(Term("field", "aaaaa"), FuzzyQuery.defaultMaxEdits, 6)
        hits = searcher.search(query, None, 1000).scoreDocs
        self.assertEqual(1, len(hits))
    
        # test scoring
        query = FuzzyQuery(Term("field", "bbbbb"), FuzzyQuery.defaultMaxEdits, 0)
        hits = searcher.search(query, None, 1000).scoreDocs
        self.assertEqual(3, len(hits), "3 documents should match")

        order = ("bbbbb", "abbbb", "aabbb")
        for hit, o in izip(hits, order):
            term = searcher.doc(hit.doc).get("field")
            self.assertEqual(o, term)

        # test pq size by supplying maxExpansions=2
        # This query would normally return 3 documents, because 3 terms match
        # (see above):
        query = FuzzyQuery(Term("field", "bbbbb"), FuzzyQuery.defaultMaxEdits,
                           0, 2, False)
        hits = searcher.search(query, None, 1000).scoreDocs
        self.assertEqual(2, len(hits), "only 2 documents should match");
        order = ("bbbbb","abbbb")
        for hit, o in izip(hits, order):
            term = searcher.doc(hit.doc).get("field")
            self.assertEqual(o, term)

        # not similar enough:
        query = FuzzyQuery(Term("field", "xxxxx"))
        topDocs = searcher.search(query, 50)
        self.assertEqual(0, topDocs.totalHits)

        # edit distance to "aaaaa" = 3
        query = FuzzyQuery(Term("field", "aaccc"))
        topDocs = searcher.search(query, 50)
        self.assertEqual(0, topDocs.totalHits)

        # query identical to a word in the index:
        query = FuzzyQuery(Term("field", "aaaaa"))
        scoreDocs = searcher.search(query, 50).scoreDocs
        self.assertEqual(3, len(scoreDocs))
        self.assertEqual(searcher.doc(scoreDocs[0].doc).get("field"), "aaaaa")

        # default allows for up to two edits:
        self.assertEqual(searcher.doc(scoreDocs[1].doc).get("field"), "aaaab")
        self.assertEqual(searcher.doc(scoreDocs[2].doc).get("field"), "aaabb")

        # query similar to a word in the index:
        query = FuzzyQuery(Term("field", "aaaac"))
        scoreDocs = searcher.search(query, 50).scoreDocs
        self.assertEqual(3, len(scoreDocs))
        self.assertEqual(searcher.doc(scoreDocs[0].doc).get("field"), "aaaaa")
        self.assertEqual(searcher.doc(scoreDocs[1].doc).get("field"), "aaaab")
        self.assertEqual(searcher.doc(scoreDocs[2].doc).get("field"), "aaabb")

        # now with prefix
        query = FuzzyQuery(Term("field", "aaaac"), FuzzyQuery.defaultMaxEdits, 1)
        hits = searcher.search(query, None, 1000).scoreDocs
        self.assertEqual(3, len(hits))
        self.assertEqual(searcher.doc(hits[0].doc).get("field"), ("aaaaa"))
        self.assertEqual(searcher.doc(hits[1].doc).get("field"), ("aaaab"))
        self.assertEqual(searcher.doc(hits[2].doc).get("field"), ("aaabb"))

        query = FuzzyQuery(Term("field", "aaaac"), FuzzyQuery.defaultMaxEdits, 2)
        hits = searcher.search(query, None, 1000).scoreDocs
        self.assertEqual(3, len(hits))
        self.assertEqual(searcher.doc(hits[0].doc).get("field"), ("aaaaa"))
        self.assertEqual(searcher.doc(hits[1].doc).get("field"), ("aaaab"))
        self.assertEqual(searcher.doc(hits[2].doc).get("field"), ("aaabb"))

        query = FuzzyQuery(Term("field", "aaaac"), FuzzyQuery.defaultMaxEdits, 3)
        hits = searcher.search(query, None, 1000).scoreDocs
        self.assertEqual(3, len(hits))
        self.assertEqual(searcher.doc(hits[0].doc).get("field"), ("aaaaa"))
        self.assertEqual(searcher.doc(hits[1].doc).get("field"), ("aaaab"))
        self.assertEqual(searcher.doc(hits[2].doc).get("field"), ("aaabb"))

        query = FuzzyQuery(Term("field", "aaaac"), FuzzyQuery.defaultMaxEdits, 4)
        hits = searcher.search(query, None, 1000).scoreDocs
        self.assertEqual(2, len(hits))
        self.assertEqual(searcher.doc(hits[0].doc).get("field"), ("aaaaa"))
        self.assertEqual(searcher.doc(hits[1].doc).get("field"), ("aaaab"))
        query = FuzzyQuery(Term("field", "aaaac"), FuzzyQuery.defaultMaxEdits, 5)
        hits = searcher.search(query, None, 1000).scoreDocs
        self.assertEqual(0, len(hits))
    
        query = FuzzyQuery(Term("field", "ddddX"), FuzzyQuery.defaultMaxEdits, 0)
        hits = searcher.search(query, None, 1000).scoreDocs
        self.assertEqual(1, len(hits))
        self.assertEqual(searcher.doc(hits[0].doc).get("field"), ("ddddd"))
    
        # now with prefix
        query = FuzzyQuery(Term("field", "ddddX"), FuzzyQuery.defaultMaxEdits, 1)
        hits = searcher.search(query, None, 1000).scoreDocs
        self.assertEqual(1, len(hits))
        self.assertEqual(searcher.doc(hits[0].doc).get("field"), ("ddddd"))

        query = FuzzyQuery(Term("field", "ddddX"), FuzzyQuery.defaultMaxEdits, 2)
        hits = searcher.search(query, None, 1000).scoreDocs
        self.assertEqual(1, len(hits))
        self.assertEqual(searcher.doc(hits[0].doc).get("field"), ("ddddd"))

        query = FuzzyQuery(Term("field", "ddddX"), FuzzyQuery.defaultMaxEdits, 3)
        hits = searcher.search(query, None, 1000).scoreDocs;
        self.assertEqual(1, len(hits))
        self.assertEqual(searcher.doc(hits[0].doc).get("field"), ("ddddd"))

        query = FuzzyQuery(Term("field", "ddddX"), FuzzyQuery.defaultMaxEdits, 4)
        hits = searcher.search(query, None, 1000).scoreDocs
        self.assertEqual(1, len(hits))
        self.assertEqual(searcher.doc(hits[0].doc).get("field"), ("ddddd"))

        query = FuzzyQuery(Term("field", "ddddX"), FuzzyQuery.defaultMaxEdits, 5)
        hits = searcher.search(query, None, 1000).scoreDocs
        self.assertEqual(0, len(hits))
    
        # different field = no match:
        query = FuzzyQuery(Term("anotherfield", "ddddX"), FuzzyQuery.defaultMaxEdits, 0)
        hits = searcher.search(query, None, 1000).scoreDocs
        self.assertEqual(0, len(hits))

    def test2(self):

      writer = self.getWriter()

      self._addDoc("LANGE", writer)
      self._addDoc("LUETH", writer)
      self._addDoc("PIRSING", writer)
      self._addDoc("RIEGEL", writer)
      self._addDoc("TRZECZIAK", writer)
      self._addDoc("WALKER", writer)
      self._addDoc("WBR", writer)
      self._addDoc("WE", writer)
      self._addDoc("WEB", writer)
      self._addDoc("WEBE", writer)
      self._addDoc("WEBER", writer)
      self._addDoc("WEBERE", writer)
      self._addDoc("WEBREE", writer)
      self._addDoc("WEBEREI", writer)
      self._addDoc("WBRE", writer)
      self._addDoc("WITTKOPF", writer)
      self._addDoc("WOJNAROWSKI", writer)
      self._addDoc("WRICKE", writer)

      reader = writer.getReader()
      searcher = self.getSearcher(reader=reader)
      writer.close()

      query = FuzzyQuery(Term("field", "WEBER"), 2, 1)
      hits = searcher.search(query, None, 1000).scoreDocs
      self.assertEqual(8, len(hits))

    def testTieBreaker(self):
      # MultiTermQuery provides (via attribute) information about which values
      # must be competitive to enter the priority queue. 
      #
      # FuzzyQuery optimizes itself around this information, if the attribute
      # is not implemented correctly, there will be problems!
      #
      directory = RAMDirectory()
      writer = self.getWriter(directory=directory)
      self._addDoc("a123456", writer)
      self._addDoc("c123456", writer)
      self._addDoc("d123456", writer)
      self._addDoc("e123456", writer)
    
      directory2 = RAMDirectory()
      writer2 = self.getWriter(directory=directory2)
      self._addDoc("a123456", writer2)
      self._addDoc("b123456", writer2)
      self._addDoc("b123456", writer2)
      self._addDoc("b123456", writer2)
      self._addDoc("c123456", writer2)
      self._addDoc("f123456", writer2)
    
      ir1 = writer.getReader()
      ir2 = writer2.getReader()
    
      mr = MultiReader([ir1, ir2])
      searcher = self.getSearcher(reader=mr)

      fq = FuzzyQuery(Term("field", "z123456"), 1, 0, 2, False)
      docs = searcher.search(fq, 2)
      self.assertEqual(5, docs.totalHits)  # 5 docs, from the a and b's

      mr.close()
      ir1.close()
      ir2.close()
      writer.close()
      writer2.close()
      directory.close()
      directory2.close()

    def testBoostOnlyRewrite(self):
        # Test the TopTermsBoostOnlyBooleanQueryRewrite rewrite method.

        writer = self.getWriter()
        self._addDoc("Lucene", writer)
        self._addDoc("Lucene", writer)
        self._addDoc("Lucenne", writer)

        reader = writer.getReader()
        searcher = self.getSearcher(reader=reader)
        writer.close()
    
        query = FuzzyQuery(Term("field", "lucene"))
        query.setRewriteMethod(MultiTermQuery.TopTermsBoostOnlyBooleanQueryRewrite(50))
        hits = searcher.search(query, None, 1000).scoreDocs
        self.assertEqual(3, len(hits))

        # normally, 'Lucenne' would be the first result as IDF will skew the score.
        self.assertEqual("Lucene", reader.document(hits[0].doc).get("field"))
        self.assertEqual("Lucene", reader.document(hits[1].doc).get("field"))
        self.assertEqual("Lucenne", reader.document(hits[2].doc).get("field"))

    def testGiga(self):

        w = self.getWriter(analyzer=StandardAnalyzer(Version.LUCENE_CURRENT))

        self._addDoc("Lucene in Action", w)
        self._addDoc("Lucene for Dummies", w)

        self._addDoc("Giga byte", w)

        self._addDoc("ManagingGigabytesManagingGigabyte", w)
        self._addDoc("ManagingGigabytesManagingGigabytes", w)

        self._addDoc("The Art of Computer Science", w)
        self._addDoc("J. K. Rowling", w)
        self._addDoc("JK Rowling", w)
        self._addDoc("Joanne K Roling", w)
        self._addDoc("Bruce Willis", w)
        self._addDoc("Willis bruce", w)
        self._addDoc("Brute willis", w)
        self._addDoc("B. willis", w)

        r = w.getReader()
        w.close()

        q = FuzzyQuery(Term("field", "giga"), 0)

        searcher = self.getSearcher(reader=r)
        hits = searcher.search(q, 10).scoreDocs

        self.assertEqual(1, len(hits))
        self.assertEqual("Giga byte", searcher.doc(hits[0].doc).get("field"))

    def testDistanceAsEditsSearching(self):

        w = self.getWriter()
        self._addDoc("foobar", w)
        self._addDoc("test", w)
        self._addDoc("working", w)

        reader = w.getReader()
        searcher = self.getSearcher(reader=reader)
        w.close()
    
        q = FuzzyQuery(Term("field", "fouba"), 2)
        hits = searcher.search(q, 10).scoreDocs
        self.assertEqual(1, len(hits))
        self.assertEqual("foobar", searcher.doc(hits[0].doc).get("field"))
    
        q = FuzzyQuery(Term("field", "foubara"), 2)
        hits = searcher.search(q, 10).scoreDocs
        self.assertEqual(1, len(hits))
        self.assertEqual("foobar", searcher.doc(hits[0].doc).get("field"))
    
        try:
            q = FuzzyQuery(Term("field", "t"), 3)
            self.fail()
        except JavaError, e:
            #expected
            pass
  

if __name__ == "__main__":
    lucene.initVM()
    if '-loop' in sys.argv:
        sys.argv.remove('-loop')
        while True:
            try:
                unittest.main()
            except:
                pass
    else:
        unittest.main()
