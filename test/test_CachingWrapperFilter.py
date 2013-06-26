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
from PyLuceneTestCase import PyLuceneTestCase

from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import \
    AtomicReaderContext, SlowCompositeReaderWrapper
from org.apache.lucene.search import CachingWrapperFilter
from org.apache.lucene.util import Version, FixedBitSet
from org.apache.pylucene.search import PythonFilter


class CachingWrapperFilterTestCase(PyLuceneTestCase):
    """
    Unit tests ported from Java Lucene
    """

    def testCachingWorks(self):
        writer = self.getWriter(analyzer=StandardAnalyzer(Version.LUCENE_CURRENT))
        writer.close()
        reader = SlowCompositeReaderWrapper.wrap(self.getReader())
        context = AtomicReaderContext.cast_(reader.getContext())

        class mockFilter(PythonFilter):
            def __init__(self):
                super(mockFilter, self).__init__()
                self._wasCalled = False
            def getDocIdSet(self, context, acceptDocs):
                self._wasCalled = True;
                return FixedBitSet(context.reader().maxDoc())
            def clear(self):
                self._wasCalled = False
            def wasCalled(self):
                return self._wasCalled

        filter = mockFilter()
        cacher = CachingWrapperFilter(filter)

        # first time, nested filter is called
        strongRef = cacher.getDocIdSet(context, context.reader().getLiveDocs())
        self.assert_(filter.wasCalled(), "first time")

        # second time, nested filter should not be called
        filter.clear()
        cacher.getDocIdSet(context, context.reader().getLiveDocs())
        self.assert_(not filter.wasCalled(), "second time")

        reader.close()


if __name__ == "__main__":
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
