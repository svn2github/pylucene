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
    Document, Field, IndexWriter, StandardAnalyzer, IntField, \
    SimpleDateFormat, Version, SimpleFSDirectory, File, DateTools, \
    IndexWriterConfig, LogMergePolicy, FieldType, TextField, StringField, \
    FieldInfo

# date culled from LuceneInAction.zip archive from Manning site
samplesModified = SimpleDateFormat('yyyy-MM-dd').parse('2004-12-02')


class TestDataDocumentHandler(object):

    def createIndex(cls, dataDir, indexDir, useCompound):

        indexDir = SimpleFSDirectory(File(indexDir))
        config = IndexWriterConfig(Version.LUCENE_CURRENT,
                             StandardAnalyzer(Version.LUCENE_CURRENT))
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        
        writer = IndexWriter(indexDir, config)
        config = writer.getConfig()
        mp = config.getMergePolicy()
        
        if (LogMergePolicy.instance_(mp)):
            mp.setUseCompoundFile(useCompound)

        for dir, dirnames, filenames in os.walk(dataDir):
            for filename in filenames:
                if filename.endswith('.properties'):
                    cls.indexFile(writer, os.path.join(dir, filename), dataDir)

        writer.commit()
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

        doc.add(Field("isbn", isbn, StringField.TYPE_STORED))
        
        doc.add(Field("category", category, StringField.TYPE_STORED))
        
        # note: ft should be initialized once and re-used
        ft = FieldType()
        ft.setIndexed(True)
        ft.setTokenized(True)
        ft.setStored(True)
        ft.setStoreTermVectorPositions(True)
        ft.setStoreTermVectorOffsets(True)
        ft.freeze()
        doc.add(Field("title", title, ft))  
                            
        ft = FieldType(StringField.TYPE_STORED)
        ft.setIndexed(True)
        ft.setTokenized(False)
        ft.setOmitNorms(True)
        ft.setStoreTermVectorPositions(True)
        ft.setStoreTermVectorOffsets(True)
        doc.add(Field("title2", title.lower(), ft))

        # split multiple authors into unique field instances
        authors = author.split(',')
        ft = FieldType()
        ft.setIndexed(True)
        ft.setTokenized(False)
        ft.setStored(True)
        ft.setStoreTermVectorPositions(True)
        ft.setStoreTermVectorOffsets(True)
        for a in authors:
            doc.add(Field("author", a, ft))

        ft = FieldType()
        ft.setIndexed(True)
        ft.setTokenized(False)
        ft.setStored(True)
        ft.setOmitNorms(True)
        doc.add(Field("url", url, ft))
        
        ft = FieldType()
        ft.setIndexed(True)
        ft.setTokenized(True)
        ft.setStored(False)
        ft.setStoreTermVectorPositions(True)
        ft.setStoreTermVectorOffsets(True)
        doc.add(Field("subject", subject, ft))
        
        doc.add(IntField("pubmonth", int(pubmonth), Field.Store.YES))

        d = DateTools.stringToDate(pubmonth)
        d = int(d.getTime() / (1000 * 3600 * 24.0))
        doc.add(IntField("pubmonthAsDay", d, IntField.TYPE_NOT_STORED))

        ft = FieldType()
        ft.setIndexed(True)
        ft.setTokenized(True)
        ft.setStored(False)
        ft.setStoreTermVectorPositions(True)
        ft.setStoreTermVectorOffsets(True)
        doc.add(Field("contents", ' '.join([title, subject, author, category]),
                      ft))

        doc.add(Field("path", path,
                      StringField.TYPE_STORED))
        
        doc.add(Field("modified", DateTools.dateToString(samplesModified, DateTools.Resolution.MILLISECOND),
                      StringField.TYPE_STORED))

        writer.addDocument(doc)

    createIndex = classmethod(createIndex)
    indexFile = classmethod(indexFile)
