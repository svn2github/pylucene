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
     SimpleAnalyzer, Document, QueryParser, Explanation, \
     IndexSearcher, FSDirectory, Hit


class Explainer(object):

    def main(cls, argv):

        if len(argv) != 3:
            print "Usage: Explainer <index dir> <query>"

        else:
            indexDir = argv[1]
            queryExpression = argv[2]

            directory = FSDirectory.getDirectory(indexDir, False)

            query = QueryParser("contents",
                                SimpleAnalyzer()).parse(queryExpression)

            print "Query:", queryExpression

            searcher = IndexSearcher(directory)
            hits = searcher.search(query)

            for hit in hits:
                hit = Hit.cast_(hit)
                doc = hit.getDocument()
                id = hit.getId()
                explanation = searcher.explain(query, id)
                print "----------"
                print doc["title"].encode('utf-8')
                print explanation

    main = classmethod(main)


if __name__ == "__main__":
    import sys
    Explainer.main(sys.argv)
