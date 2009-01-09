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

from lucene import \
     WhitespaceAnalyzer, Document, Field, IndexReader, IndexWriter


class T9er(object):

    keys = [         "2abc", "3def",
            "4ghi",  "5jkl", "6mno",
            "7pqrs", "8tuv", "9wxyz"]

    keyMap = {}

    def main(cls, argv):
        
        if len(argv) != 3:
            print "Usage: T9er <WordNet index dir> <t9 index>"
            return
        
        for key in cls.keys:
            c = key[0]
            k = key[1:]
            for kc in k:
                cls.keyMap[kc] = c
                print kc, "=", c

        indexDir = argv[1]
        t9dir = argv[2]

        reader = IndexReader.open(indexDir)

        numDocs = reader.maxDoc()
        print "Processing", numDocs, "words"

        writer = IndexWriter(t9dir, WhitespaceAnalyzer(), True)

        for id in xrange(reader.maxDoc()):
            origDoc = reader.document(id)
            word = origDoc.get("word")
            if word is None or len(word) == 0:
                continue

            newDoc = Document()
            newDoc.add(Field("word", word,
                             Field.Store.YES, Field.Index.UN_TOKENIZED))
            newDoc.add(Field("t9", cls.t9(word),
                             Field.Store.YES, Field.Index.UN_TOKENIZED))
            newDoc.add(Field("length", str(len(word)),
                             Field.Store.NO, Field.Index.UN_TOKENIZED))
            writer.addDocument(newDoc)
            if id % 100 == 0:
                print "Document", id

        writer.optimize()
        writer.close()

        reader.close()

    def t9(cls, word):

        return ''.join([cls.keyMap[c] for c in word])

    main = classmethod(main)
    t9 = classmethod(t9)
