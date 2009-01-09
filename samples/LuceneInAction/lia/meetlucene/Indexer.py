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
    IndexWriter, StandardAnalyzer, Document, Field, \
    InputStreamReader, FileInputStream


class Indexer(object):

    def main(cls, argv):

        if len(argv) != 3:
            print "Usage: python Indexer.py <index dir> <data dir>"

        else:
            indexDir = argv[1]
            dataDir = argv[2]

            start = time()
            numIndexed = cls.index(indexDir, dataDir)
            duration = timedelta(seconds=time() - start)

            print "Indexing %s files took %s" %(numIndexed, duration)

    def index(cls, indexDir, dataDir):

        if not (os.path.exists(dataDir) and os.path.isdir(dataDir)):
            raise IOError, "%s does not exist or is not a directory" %(dataDir)

        writer = IndexWriter(indexDir, StandardAnalyzer(), True)
        writer.setUseCompoundFile(False)

        cls.indexDirectory(writer, dataDir)

        numIndexed = writer.docCount()
        writer.optimize()
        writer.close()

        return numIndexed

    def indexDirectory(cls, writer, dir):

        for name in os.listdir(dir):
            path = os.path.join(dir, name)
            if os.path.isfile(path):
                if path.endswith('.txt'):
                    cls.indexFile(writer, path)
            elif os.path.isdir(path):
                cls.indexDirectory(writer, path)

    def indexFile(cls, writer, path):

        try:
            reader = InputStreamReader(FileInputStream(path), 'iso-8859-1')
        except IOError, e:
            print 'IOError while opening %s: %s' %(path, e)
        else:
            print 'Indexing', path
            doc = Document()
            doc.add(Field("contents", reader))
            doc.add(Field("path", os.path.abspath(path),
                          Field.Store.YES, Field.Index.UN_TOKENIZED))
            writer.addDocument(doc)
            reader.close()

    main = classmethod(main)
    index = classmethod(index)
    indexDirectory = classmethod(indexDirectory)
    indexFile = classmethod(indexFile)


if __name__ == "__main__":
    import sys
    Indexer.main(sys.argv)
