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

import lucene
from unittest import TestCase

from java.io import File
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.document import Field
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.index import \
    IndexWriter, IndexWriterConfig, DirectoryReader
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.store import RAMDirectory
from org.apache.lucene.util import Version


class PyLuceneTestCase(TestCase):

    def __init__(self, *args):
        super(PyLuceneTestCase, self).__init__(*args)
        self.TEST_VERSION = Version.LUCENE_CURRENT

    def setUp(self):
        self.directory = RAMDirectory()

    def tearDown(self):
        self.directory.close()
        
    def getWriter(self, directory=None, analyzer=None, open_mode=None):
        config = IndexWriterConfig(self.TEST_VERSION,
                                   analyzer or LimitTokenCountAnalyzer(WhitespaceAnalyzer(Version.LUCENE_CURRENT), 10000))
        config.setOpenMode(open_mode or IndexWriterConfig.OpenMode.CREATE)

        return IndexWriter(directory or self.directory, config)
        
    def getSearcher(self, directory=None, reader=None):
        if reader is not None:
            return IndexSearcher(reader)
        return IndexSearcher(self.getReader(directory=directory))
    
    def getReader(self, directory=None):
        return DirectoryReader.open(directory or self.directory)

    def newField(self, name, value, type):
        return Field(name, value, type)
