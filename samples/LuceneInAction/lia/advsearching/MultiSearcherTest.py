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
     RangeQuery, RAMDirectory, IndexSearcher


class MultiSearcherTest(TestCase):

    def setUp(self):
        
        animals = [ "aardvark", "beaver", "coati",
                    "dog", "elephant", "frog", "gila monster",
                    "horse", "iguana", "javelina", "kangaroo",
                    "lemur", "moose", "nematode", "orca",
                    "python", "quokka", "rat", "scorpion",
                    "tarantula", "uromastyx", "vicuna",
                    "walrus", "xiphias", "yak", "zebra" ]

        analyzer = WhitespaceAnalyzer()

        aTOmDirectory = RAMDirectory()
        nTOzDirectory = RAMDirectory()

        aTOmWriter = IndexWriter(aTOmDirectory, analyzer, True)
        nTOzWriter = IndexWriter(nTOzDirectory, analyzer, True)

        for animal in animals:
            doc = Document()
            doc.add(Field("animal", animal,
                          Field.Store.YES, Field.Index.UN_TOKENIZED))

            if animal[0].lower() < "n":
                aTOmWriter.addDocument(doc)
            else:
                nTOzWriter.addDocument(doc)

        aTOmWriter.close()
        nTOzWriter.close()

        self.searchers = [ IndexSearcher(aTOmDirectory),
                           IndexSearcher(nTOzDirectory) ]

    def testMulti(self):

        searcher = MultiSearcher(self.searchers)

        # range spans documents across both indexes
        query = RangeQuery(Term("animal", "h"), Term("animal", "t"), True)

        hits = searcher.search(query)
        self.assertEqual(12, hits.length(), "tarantula not included")
