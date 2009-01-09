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

from time import time
from datetime import timedelta

from lucene import \
     Document, IndexSearcher, FSDirectory, QueryParser, StandardAnalyzer, Hit


class Searcher(object):

    def main(cls, argv):

        if len(argv) != 3:
            print "Usage: python Searcher.py <index dir> <query>"

        else:
            indexDir = argv[1]
            q = argv[2]

            if not (os.path.exists(indexDir) and os.path.isdir(indexDir)):
                raise IOError, "%s does not exist or is not a directory" %(indexDir)

            cls.search(indexDir, q)

    def search(cls, indexDir, q):

        fsDir = FSDirectory.getDirectory(indexDir, False)
        searcher = IndexSearcher(fsDir)

        query = QueryParser("contents", StandardAnalyzer()).parse(q)
        start = time()
        hits = searcher.search(query)
        duration = timedelta(seconds=time() - start)

        print "Found %d document(s) (in %s) that matched query '%s':" %(hits.length(), duration, q)

        for hit in hits:
            doc = Hit.cast_(hit).getDocument()
            print doc["path"]

    main = classmethod(main)
    search = classmethod(search)


if __name__ == "__main__":
    import sys
    Searcher.main(sys.argv)
