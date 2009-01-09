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


class PrefixFilterTestCase(TestCase):
    """
    Unit tests ported from Java Lucene
    """

    def testPrefixFilter(self):

        directory = RAMDirectory()

        categories = ["/Computers/Linux",
                      "/Computers/Mac/One",
                      "/Computers/Mac/Two",
                      "/Computers/Windows"]

        writer = IndexWriter(directory, WhitespaceAnalyzer(), True)

        for category in categories:
            doc = Document()
            doc.add(Field("category", category,
                          Field.Store.YES, Field.Index.UN_TOKENIZED))
            writer.addDocument(doc)

        writer.close()

        # PrefixFilter combined with ConstantScoreQuery
        filter = PrefixFilter(Term("category", "/Computers"))
        query = ConstantScoreQuery(filter)
        searcher = IndexSearcher(directory)
        hits = searcher.search(query)
        self.assertEqual(4, hits.length(),
                         "All documents in /Computers category and below")

        # test middle of values
        filter = PrefixFilter(Term("category", "/Computers/Mac"))
        query = ConstantScoreQuery(filter)
        hits = searcher.search(query)
        self.assertEqual(2, hits.length(), "Two in /Computers/Mac")

        # test start of values
        filter = PrefixFilter(Term("category", "/Computers/Linux"))
        query = ConstantScoreQuery(filter)
        hits = searcher.search(query)
        self.assertEqual(1, hits.length(), "One in /Computers/Linux")

        # test end of values
        filter = PrefixFilter(Term("category", "/Computers/Windows"))
        query = ConstantScoreQuery(filter)
        hits = searcher.search(query)
        self.assertEqual(1, hits.length(), "One in /Computers/Windows")

        # test non-existant
        filter = PrefixFilter(Term("category", "/Computers/ObsoleteOS"))
        query = ConstantScoreQuery(filter)
        hits = searcher.search(query)
        self.assertEqual(0, hits.length(), "no documents")

        # test non-existant, before values
        filter = PrefixFilter(Term("category", "/Computers/AAA"))
        query = ConstantScoreQuery(filter)
        hits = searcher.search(query)
        self.assertEqual(0, hits.length(), "no documents")

        # test non-existant, after values
        filter = PrefixFilter(Term("category", "/Computers/ZZZ"))
        query = ConstantScoreQuery(filter)
        hits = searcher.search(query)
        self.assertEqual(0, hits.length(), "no documents")

        # test zero-length prefix
        filter = PrefixFilter(Term("category", ""))
        query = ConstantScoreQuery(filter)
        hits = searcher.search(query)
        self.assertEqual(4, hits.length(), "all documents")

        # test non-existant field
        filter = PrefixFilter(Term("nonexistantfield", "/Computers"))
        query = ConstantScoreQuery(filter)
        hits = searcher.search(query)
        self.assertEqual(0, hits.length(), "no documents")


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
