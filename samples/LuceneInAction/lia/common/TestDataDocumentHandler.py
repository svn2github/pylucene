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
    Document, Field, IndexWriter, StandardAnalyzer, DateField, \
    SimpleDateFormat

# date culled from LuceneInAction.zip archive from Manning site
samplesModified = SimpleDateFormat('yyyy-MM-dd').parse('2004-12-02')


class TestDataDocumentHandler(object):

    def createIndex(cls, dataDir, indexDir, useCompound):

        writer = IndexWriter(indexDir, StandardAnalyzer(), True)
        writer.setUseCompoundFile(useCompound)

        for dir, dirnames, filenames in os.walk(dataDir):
            for filename in filenames:
                if filename.endswith('.properties'):
                    cls.indexFile(writer, os.path.join(dir, filename), dataDir)

        writer.optimize()
        writer.close()

    def indexFile(cls, writer, path, baseDir):
        
        input = file(path)
        props = {}
        while True:
            line = input.readline().strip()
            if not line:
                break
            name, value = line.split('=', 1)
            props[name] = value.decode('unicode-escape')
        input.close()

        doc = Document()

        # category comes from relative path below the base directory
        category = os.path.dirname(path)[len(baseDir):]
        if os.path.sep != '/':
            category = category.replace(os.path.sep, '/')

        isbn = props['isbn']
        title = props['title']
        author = props['author']
        url = props['url']
        subject = props['subject']
        pubmonth = props['pubmonth']

        print title.encode('utf8')
        print author.encode('utf-8')
        print subject.encode('utf-8')
        print category.encode('utf-8')
        print "---------"

        doc.add(Field("isbn", isbn,
                      Field.Store.YES, Field.Index.UN_TOKENIZED))
        doc.add(Field("category", category,
                      Field.Store.YES, Field.Index.UN_TOKENIZED))
        doc.add(Field("title", title,
                      Field.Store.YES, Field.Index.TOKENIZED))

        # split multiple authors into unique field instances
        authors = author.split(',')
        for a in authors:
            doc.add(Field("author", a,
                          Field.Store.YES, Field.Index.UN_TOKENIZED))

        doc.add(Field("url", url,
                      Field.Store.YES, Field.Index.NO))
        doc.add(Field("subject", subject,
                      Field.Store.NO, Field.Index.TOKENIZED,
                      Field.TermVector.YES))
        doc.add(Field("pubmonth", pubmonth,
                      Field.Store.YES, Field.Index.UN_TOKENIZED))
        doc.add(Field("contents", ' '.join([title, subject, author]),
                      Field.Store.NO, Field.Index.TOKENIZED))

        doc.add(Field("path", path,
                      Field.Store.YES, Field.Index.UN_TOKENIZED))
        doc.add(Field("modified", DateField.dateToString(samplesModified),
                      Field.Store.YES, Field.Index.UN_TOKENIZED))

        writer.addDocument(doc)

    createIndex = classmethod(createIndex)
    indexFile = classmethod(indexFile)
