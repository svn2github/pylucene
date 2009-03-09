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

from lia.common.LiaTestCase import LiaTestCase
from lia.extsearch.hitcollector.BookLinkCollector import BookLinkCollector

from lucene import IndexSearcher, TermQuery, Term

class HitCollectorTest(LiaTestCase):

    def testCollecting(self):

        query = TermQuery(Term("contents", "junit"))
        searcher = IndexSearcher(self.directory)

        collector = BookLinkCollector(searcher)
        searcher.search(query, collector)

        links = collector.getLinks()
        self.assertEqual("Java Development with Ant",
                         links["http://www.manning.com/antbook"])

        hits = searcher.search(query)
        self.dumpHits(hits)

        searcher.close()
