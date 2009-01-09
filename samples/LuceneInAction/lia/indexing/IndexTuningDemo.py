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
     IndexWriter, SimpleAnalyzer, Document, Field, Term, FSDirectory, System


class IndexTuningDemo(object):

    def main(cls, argv):

        if len(argv) < 5:
            print "Usage: python IndexTuningDemo.py <numDocs> <mergeFactor> <maxMergeDocs> <maxBufferedDocs>"
            return
            
        docsInIndex  = int(argv[1])

        # create an index called 'index-dir' in a temp directory
        indexDir = os.path.join(System.getProperty('java.io.tmpdir', 'tmp'),
                                'index-dir')
        dir = FSDirectory.getDirectory(indexDir, True)
        analyzer = SimpleAnalyzer()
        writer = IndexWriter(dir, analyzer, True)

        # set variables that affect speed of indexing
        writer.setMergeFactor(int(argv[2]))
        writer.setMaxMergeDocs(int(argv[3]))
        writer.setMaxBufferedDocs(int(argv[4]))
        # writer.infoStream = System.out

        print "Merge factor:  ", writer.getMergeFactor()
        print "Max merge docs:", writer.getMaxMergeDocs()
        print "Max buffered docs:", writer.getMaxBufferedDocs()

        start = time()
        for i in xrange(docsInIndex):
            doc = Document()
            doc.add(Field("fieldname", "Bibamus",
                          Field.Store.YES, Field.Index.TOKENIZED))
            writer.addDocument(doc)

        writer.close()
        print "Time: ", timedelta(seconds=time() - start)

    main = classmethod(main)
