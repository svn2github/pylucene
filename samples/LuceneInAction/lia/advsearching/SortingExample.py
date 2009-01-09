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
