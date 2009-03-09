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

from lucene import Document, IndexSearcher, PythonHitCollector

#
# A HitCollector extension
#

class BookLinkCollector(PythonHitCollector):

    def __init__(self, searcher):
        super(BookLinkCollector, self).__init__()
        self.searcher = searcher
        self.documents = {}

    def collect(self, id, score):

        doc = self.searcher.doc(id);
        self.documents[doc["url"]] = doc["title"]

        print "%s: %s" %(doc['title'], score)

    def getLinks(self):

        return self.documents.copy()
