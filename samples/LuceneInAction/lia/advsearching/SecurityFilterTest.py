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

from unittest import TestCase
from lucene import \
     WhitespaceAnalyzer, Document, Field, IndexWriter, Term, MultiSearcher, \
     QueryFilter, RAMDirectory, IndexSearcher, TermQuery


class SecurityFilterTest(TestCase):

    def setUp(self):

        self.directory = RAMDirectory()
        writer = IndexWriter(self.directory, WhitespaceAnalyzer(), True)

        # Elwood
        document = Document()
        document.add(Field("owner", "elwood",
                           Field.Store.YES, Field.Index.UN_TOKENIZED))
        document.add(Field("keywords", "elwoods sensitive info",
                           Field.Store.YES, Field.Index.TOKENIZED))
        writer.addDocument(document)

        # Jake
        document = Document()
        document.add(Field("owner", "jake",
                           Field.Store.YES, Field.Index.UN_TOKENIZED))
        document.add(Field("keywords", "jakes sensitive info",
                           Field.Store.YES, Field.Index.TOKENIZED))
        writer.addDocument(document)

        writer.close()

    def testSecurityFilter(self):

        query = TermQuery(Term("keywords", "info"))

        searcher = IndexSearcher(self.directory)
        hits = searcher.search(query)
        self.assertEqual(2, len(hits), "Both documents match")

        jakeFilter = QueryFilter(TermQuery(Term("owner", "jake")))

        hits = searcher.search(query, jakeFilter)
        self.assertEqual(1, len(hits))
        self.assertEqual("jakes sensitive info", hits[0].get("keywords"),
                         "elwood is safe")
