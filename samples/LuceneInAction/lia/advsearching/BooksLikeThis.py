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
     Document, IndexReader, Term, BooleanQuery, IndexSearcher, TermQuery, \
     FSDirectory, System, BooleanClause, Hit


class BooksLikeThis(object):

    def main(cls, argv):

        indexDir = System.getProperty("index.dir")
        directory = FSDirectory.getDirectory(indexDir, False)

        reader = IndexReader.open(directory)
        blt = BooksLikeThis(reader)

        for id in xrange(reader.maxDoc()):
            if reader.isDeleted(id):
                continue
            doc = reader.document(id)
            print ''
            print doc.get("title").encode('utf-8')

            docs = blt.docsLike(id, doc, 10)
            if not docs:
                print "  None like this"
            else:
                for doc in docs:
                    print " ->", doc.get("title").encode('utf-8')

    def __init__(self, reader):

        self.reader = reader
        self.searcher = IndexSearcher(reader)

    def docsLike(self, id, doc, max):

        authors = doc.getValues("author")
        authorQuery = BooleanQuery()
        for author in authors:
            authorQuery.add(TermQuery(Term("author", author)),
                            BooleanClause.Occur.SHOULD)
        authorQuery.setBoost(2.0)

        vector = self.reader.getTermFreqVector(id, "subject")

        subjectQuery = BooleanQuery()
        for term in vector.getTerms():
            tq = TermQuery(Term("subject", term))
            subjectQuery.add(tq, BooleanClause.Occur.SHOULD)

        likeThisQuery = BooleanQuery()
        likeThisQuery.add(authorQuery, BooleanClause.Occur.SHOULD)
        likeThisQuery.add(subjectQuery, BooleanClause.Occur.SHOULD)

        # exclude myself
        likeThisQuery.add(TermQuery(Term("isbn", doc.get("isbn"))),
                          BooleanClause.Occur.MUST_NOT)

        print "  Query:", likeThisQuery.toString("contents")
        hits = self.searcher.search(likeThisQuery)

        docs = []
        for hit in hits:
            hit = Hit.cast_(hit)
            doc = hit.getDocument()
            if len(docs) < max:
                docs.append(doc)
            else:
                break

        return docs

    main = classmethod(main)
