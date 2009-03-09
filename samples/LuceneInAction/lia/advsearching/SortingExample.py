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

import os

from lucene import \
     FSDirectory, Document, Field, IndexSearcher, SimpleAnalyzer, \
     RangeQuery, Sort, SortField, DecimalFormat, System, Term


class SortingExample(object):

    def __init__(self, directory):

        self.directory = directory

    def displayHits(self, query, sort):

        searcher = IndexSearcher(self.directory)
        hits = searcher.search(query, sort)

        print "\nResults for:", query, "sorted by", sort
        print "Title".rjust(30), "pubmonth".rjust(10), \
              "id".center(4), "score".center(15)

        scoreFormatter = DecimalFormat("0.######")
        for i, doc in hits:
            title = doc["title"]
            if len(title) > 30:
                title = title[:30]
            print title.encode('ascii', 'replace').rjust(30), \
                  doc["pubmonth"].rjust(10), \
                  str(hits.id(i)).center(4), \
                  scoreFormatter.format(hits.score(i)).ljust(12)
            print "  ", doc["category"]
            # print searcher.explain(query, hits.id(i))

        searcher.close()

    def main(cls, argv):

        earliest = Term("pubmonth", "190001")
        latest = Term("pubmonth", "201012")
        allBooks = RangeQuery(earliest, latest, True)

        indexDir = System.getProperty("index.dir")
        directory = FSDirectory.getDirectory(indexDir, False)
        example = SortingExample(directory)

        example.displayHits(allBooks, Sort.RELEVANCE)
        example.displayHits(allBooks, Sort.INDEXORDER)
        example.displayHits(allBooks, Sort("category"))
        example.displayHits(allBooks, Sort("pubmonth", True))

        example.displayHits(allBooks,
                            Sort([SortField("category"),
                                  SortField.FIELD_SCORE,
                                  SortField("pubmonth", SortField.INT, True)]))

        example.displayHits(allBooks,
                            Sort([SortField.FIELD_SCORE,
                                  SortField("category")]))

    main = classmethod(main)
