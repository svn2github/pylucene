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

import sys, lucene, unittest
from lucene import JArray
from PyLuceneTestCase import PyLuceneTestCase

from org.apache.lucene.document import Document, StoredField, Field, FieldType
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import IndexWriter
from org.apache.lucene.util import Version


class TestBinaryDocument(PyLuceneTestCase):

    binaryValStored = "this text will be stored as a byte array in the index"
    binaryValCompressed = "this text will be also stored and compressed as a byte array in the index"

    def testBinaryFieldInIndex(self):

        ft = FieldType()
        ft.setStored(True)

        bytes = JArray('byte')(self.binaryValStored)
        binaryFldStored = StoredField("binaryStored", bytes)
        stringFldStored = Field("stringStored", self.binaryValStored, ft)

        doc = Document()
        doc.add(binaryFldStored)
        doc.add(stringFldStored)

        # test for field count
        self.assertEqual(2, doc.fields.size())

        # add the doc to a ram index
        writer = self.getWriter(analyzer=StandardAnalyzer())
        writer.addDocument(doc)
        writer.close()

        # open a reader and fetch the document
        reader = self.getReader()
        docFromReader = reader.document(0)
        self.assert_(docFromReader is not None)

        # fetch the binary stored field and compare it's content with the
        # original one
        bytes = docFromReader.getBinaryValue("binaryStored")
        binaryFldStoredTest = bytes.bytes.string_
        self.assertEqual(binaryFldStoredTest, self.binaryValStored)

        # fetch the string field and compare it's content with the original
        # one
        stringFldStoredTest = docFromReader.get("stringStored")
        self.assertEqual(stringFldStoredTest, self.binaryValStored)

        reader.close()


if __name__ == '__main__':
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    if '-loop' in sys.argv:
        sys.argv.remove('-loop')
        while True:
            try:
                unittest.main()
            except:
                pass
    else:
        unittest.main()
