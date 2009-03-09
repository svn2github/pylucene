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

from unittest import TestCase, main
from lucene import Document, Field, StandardAnalyzer, IndexModifier

MinSizeForCompress = 50

class CompressTestCase(TestCase):

    def addField(self, doc, name, value):

        if len(value) > MinSizeForCompress:
            storeFlag = Field.Store.COMPRESS
        else:
            storeFlag = Field.Store.YES

        doc.add(Field(name, value, storeFlag, Field.Index.TOKENIZED))

    def indexData(self, idx, data):

        doc = Document()
        for key, val in data.iteritems():
            self.addField(doc, key, val)
            idx.addDocument(doc)

    def writeData(self, indexdir, data):

        idx = IndexModifier(indexdir, StandardAnalyzer(), True)
        idx.setUseCompoundFile(True)
        self.indexData(idx, data)
        idx.close()

    def testCompress(self):

        indexdir = 't'
        data = {'uri': "/testing/dict/index/",
                'title': "dict index example",
                'contents': "This index uses PyLucene, and writes dict data in the index."}

        self.writeData(indexdir, data)


if __name__ == "__main__":
    import sys, lucene
    lucene.initVM(lucene.CLASSPATH)
    if '-loop' in sys.argv:
        sys.argv.remove('-loop')
        while True:
            try:
                main()
            except:
                pass
    else:
        main()
