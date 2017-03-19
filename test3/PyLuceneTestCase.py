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

import lucene   # so that 'org' is found

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

    def setUp(self):
        self.directory = RAMDirectory()

    def tearDown(self):
        self.directory.close()

    def getConfig(self, analyzer=None):
        return IndexWriterConfig(analyzer)

    def getWriter(self, directory=None, analyzer=None, open_mode=None,
                  similarity=None, maxBufferedDocs=None, mergePolicy=None):
        if analyzer is None:
            analyzer = LimitTokenCountAnalyzer(WhitespaceAnalyzer(), 10000)
        config = self.getConfig(analyzer)

        if open_mode is None:
            open_mode = IndexWriterConfig.OpenMode.CREATE
        config.setOpenMode(open_mode)
        if similarity is not None:
            config.setSimilarity(similarity)
        if maxBufferedDocs is not None:
            config.setMaxBufferedDocs(maxBufferedDocs)
        if mergePolicy is not None:
            config.setMergePolicy(mergePolicy)

        if directory is None:
            directory = self.directory

        return IndexWriter(directory, config)

    def getSearcher(self, directory=None, reader=None):
        if reader is not None:
            return IndexSearcher(reader)
        return IndexSearcher(self.getReader(directory=directory))

    def getReader(self, directory=None):
        if directory is None:
            directory = self.directory
        return DirectoryReader.open(directory)

    def getOnlyLeafReader(self, reader):
        subReaders = reader.leaves()
        if subReaders.size() != 1:
            raise ValueError(reader + " has " + subReaders.size() +
                             " segments instead of exactly one")
        return subReaders.get(0).reader()
